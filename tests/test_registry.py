"""Tests for the model registry."""

import pytest

import pylometree  # triggers published.py population
from pylometree.registry import ModelEntry, registry


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
