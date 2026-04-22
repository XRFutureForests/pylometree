"""Tests for the model registry."""

import pytest

import pylometree  # triggers published.py population
from pylometree.registry import ModelEntry, ModelRegistry, registry


class TestRegistry:
    def test_populated(self):
        assert len(registry) > 5

    def test_get_chave2014(self):
        entry = registry.get("chave2014_pantropical")
        assert entry.model_type == "agb"
        assert entry.pub_year == 2014

    def test_get_missing_raises(self):
        with pytest.raises(KeyError):
            registry.get("nonexistent_model_xyz")

    def test_query_by_type(self):
        agb_models = registry.query(model_type="agb")
        assert len(agb_models) > 0
        assert all(m.model_type == "agb" for m in agb_models)

    def test_query_by_region(self):
        tropical = registry.query(region="pantropical")
        assert len(tropical) > 0

    def test_query_by_species(self):
        musa = registry.query(species="Musa")
        assert len(musa) > 0

    def test_predict_chave(self):
        entry = registry.get("chave2014_pantropical")
        agb = entry.predict(dsob=20.0, hst=18.0, rho=0.55)
        assert 100 < agb < 600  # kg

    def test_call_syntax(self):
        entry = registry.get("chave2014_pantropical")
        # __call__ == predict
        agb = entry(dsob=20.0, hst=18.0, rho=0.55)
        assert agb > 0

    def test_summary_keys(self):
        s = registry.summary()
        assert "total" in s
        assert "by_type" in s
        assert s["total"] > 0

    def test_list_ids(self):
        ids = registry.list_ids()
        assert isinstance(ids, list)
        assert "chave2014_pantropical" in ids

    def test_repr(self):
        assert "ModelRegistry" in repr(registry)

    def test_query_by_response(self):
        results = registry.query(response="agb")
        assert all("agb" in e.response.lower() for e in results)
        assert len(results) > 0

    def test_query_pub_year_min(self):
        recent = registry.query(pub_year_min=2010)
        assert all(e.pub_year is None or e.pub_year >= 2010 for e in recent)

    def test_registry_call_shortcut(self):
        # registry("id", **kwargs) ≡ registry.get("id").predict(**kwargs)
        agb_direct = registry.get("chave2014_pantropical").predict(
            dsob=20.0, hst=18.0, rho=0.55
        )
        agb_shortcut = registry("chave2014_pantropical", dsob=20.0, hst=18.0, rho=0.55)
        assert agb_direct == pytest.approx(agb_shortcut)

    def test_predict_missing_covariate_raises(self):
        entry = registry.get("chave2014_pantropical")
        with pytest.raises(ValueError, match="Missing covariate"):
            entry.predict(dsob=20.0)  # missing hst and rho

    def test_len(self):
        assert len(registry) > 5


class TestModelEntry:
    def test_to_dict_keys(self):
        entry = registry.get("chave2014_pantropical")
        d = entry.to_dict()
        required = {
            "model_id", "model_type", "equation_form", "response",
            "covariates", "parameters", "species", "region",
            "reference", "pub_year", "units", "notes",
        }
        assert required <= set(d.keys())

    def test_to_dict_values_match(self):
        entry = registry.get("chave2014_pantropical")
        d = entry.to_dict()
        assert d["model_id"] == entry.model_id
        assert d["model_type"] == entry.model_type
        assert d["covariates"] == entry.covariates

    def test_repr_contains_id(self):
        entry = registry.get("chave2014_pantropical")
        r = repr(entry)
        assert "chave2014_pantropical" in r

    def test_call_equals_predict(self):
        entry = registry.get("chave2014_pantropical")
        v1 = entry.predict(dsob=25.0, hst=22.0, rho=0.60)
        v2 = entry(dsob=25.0, hst=22.0, rho=0.60)
        assert v1 == pytest.approx(v2)


class TestModelRegistryIsolated:
    """Tests against a fresh registry instance."""

    def _make_entry(self, model_id: str = "test_model", model_type: str = "agb"):
        return ModelEntry(
            model_id=model_id,
            model_type=model_type,
            equation_form="y = a*x",
            response="agb",
            covariates=["x"],
            parameters={"a": 2.0},
            fn=lambda x, a: a * x,
            species=["Testus exampleus"],
            region=["temperate_europe"],
            pub_year=2020,
        )

    def test_register_and_get(self):
        reg = ModelRegistry()
        entry = self._make_entry()
        reg.register(entry)
        assert reg.get("test_model") is entry

    def test_register_many(self):
        reg = ModelRegistry()
        entries = [self._make_entry(f"m{i}") for i in range(3)]
        reg.register_many(entries)
        assert len(reg) == 3

    def test_get_missing_raises_keyerror(self):
        reg = ModelRegistry()
        with pytest.raises(KeyError):
            reg.get("no_such_model")

    def test_summary_counts_by_type(self):
        reg = ModelRegistry()
        reg.register(self._make_entry("a1", "agb"))
        reg.register(self._make_entry("a2", "agb"))
        reg.register(self._make_entry("h1", "hd"))
        s = reg.summary()
        assert s["total"] == 3
        assert s["by_type"]["agb"] == 2
        assert s["by_type"]["hd"] == 1

    def test_list_ids_sorted(self):
        reg = ModelRegistry()
        reg.register_many([self._make_entry("z_model"), self._make_entry("a_model")])
        ids = reg.list_ids()
        assert ids == sorted(ids)

    def test_summary_df_requires_pandas(self):
        pd = pytest.importorskip("pandas")
        reg = ModelRegistry()
        reg.register(self._make_entry())
        df = reg.summary_df()
        assert isinstance(df, pd.DataFrame)
        assert "model_id" in df.columns
