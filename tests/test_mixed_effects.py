"""Tests for mixed effects models."""

import numpy as np
import pandas as pd
import pytest

from pylometree.fitting.mixed_effects import (
    MixedEffectsModel,
    MixedFitResult,
    RandomInterceptModel,
)


class TestMixedEffectsModel:
    """Tests for MixedEffectsModel class."""

    @pytest.fixture
    def hierarchical_data(self):
        """Create sample hierarchical data."""
        np.random.seed(42)
        n_sites = 5
        n_plots_per_site = 4
        n_trees_per_plot = 10

        data = []
        for site in range(n_sites):
            site_effect = np.random.normal(0, 0.5)
            for plot in range(n_plots_per_site):
                plot_effect = np.random.normal(0, 0.3)
                for tree in range(n_trees_per_plot):
                    dbh = np.random.uniform(10, 50)
                    height = (
                        2
                        + 0.8 * np.log(dbh)
                        + site_effect
                        + plot_effect
                        + np.random.normal(0, 0.2)
                    )
                    data.append(
                        {"site": site, "plot": plot, "dbh": dbh, "height": height}
                    )

        return pd.DataFrame(data)

    def test_initialization(self, hierarchical_data):
        """Test model initialization."""
        model = MixedEffectsModel(
            formula="height ~ np.log(dbh)",
            random_effects=["site"],
            data=hierarchical_data,
        )

        assert model.formula == "height ~ np.log(dbh)"
        assert model.random_effects == ["site"]
        assert len(model.data) == len(hierarchical_data)

    def test_fit_linear_mixed_model(self, hierarchical_data):
        """Test fitting a linear mixed effects model."""
        model = MixedEffectsModel(
            formula="height ~ np.log(dbh)",
            random_effects=["site"],
            data=hierarchical_data,
        )

        result = model.fit()

        assert isinstance(result, MixedFitResult)
        assert result.n_obs == len(hierarchical_data)
        assert "np.log(dbh)" in result.params
        assert result.variance_components  # Should have variance components

    def test_fit_with_multiple_random_effects(self, hierarchical_data):
        """Test fitting with multiple random effects.
        
        Note: statsmodels MixedLM only supports ONE grouping variable directly.
        Multiple random_effects names are tracked for metadata but only the 
        first one is used as the actual groups parameter in MixedLM.
        """
        model = MixedEffectsModel(
            formula="height ~ np.log(dbh)",
            random_effects=["site", "plot"],
            data=hierarchical_data,
        )

        result = model.fit()

        assert isinstance(result, MixedFitResult)
        # Both are tracked in metadata
        assert "site" in result.random_effects
        assert "plot" in result.random_effects
        # But statsmodels only supports 1 grouping variable
        # So we get 1 variance component from the single fitted model
        assert len(result.variance_components) == 1
    def test_fit_with_method(self, hierarchical_data):
        """Test fitting with default method (REML is default in MixedLM)."""
        model = MixedEffectsModel(
            formula="height ~ np.log(dbh)",
            random_effects=["site"],
            data=hierarchical_data,
        )

        # Test default fit (uses REML internally)
        result = model.fit()
        assert result.log_likelihood is not None

    def test_predict(self, hierarchical_data):
        """Test prediction with fitted model."""
        model = MixedEffectsModel(
            formula="height ~ np.log(dbh)",
            random_effects=["site"],
            data=hierarchical_data,
        )

        result = model.fit()

        # Create test data
        test_data = pd.DataFrame({"dbh": [20, 30, 40]})

        predictions = result.predict(test_data)

        assert isinstance(predictions, np.ndarray)
        assert len(predictions) == 3
        assert all(np.isfinite(predictions))

    def test_summary(self, hierarchical_data):
        """Test summary generation."""
        model = MixedEffectsModel(
            formula="height ~ np.log(dbh)",
            random_effects=["site"],
            data=hierarchical_data,
        )

        result = model.fit()
        summary = model.summary()

        assert isinstance(summary, str)
        assert "Mixed Effects Model Summary" in summary
        assert "Fixed Effects:" in summary
        assert "Variance Components:" in summary
        assert "Model Fit:" in summary

    def test_unfitted_model_predict_raises(self, hierarchical_data):
        """Test that prediction on unfitted model raises error."""
        model = MixedEffectsModel(
            formula="height ~ np.log(dbh)",
            random_effects=["site"],
            data=hierarchical_data,
        )

        test_data = pd.DataFrame({"dbh": [20, 30, 40]})

        with pytest.raises(ValueError, match="Model must be fitted"):
            model.predict(test_data)

    def test_unfitted_model_summary_raises(self, hierarchical_data):
        """Test that summary on unfitted model raises error."""
        model = MixedEffectsModel(
            formula="height ~ np.log(dbh)",
            random_effects=["site"],
            data=hierarchical_data,
        )

        with pytest.raises(ValueError, match="Model must be fitted"):
            model.summary()


class TestRandomInterceptModel:
    """Tests for RandomInterceptModel class."""

    @pytest.fixture
    def hierarchical_data(self):
        """Create sample hierarchical data."""
        np.random.seed(42)
        n_sites = 5
        n_trees_per_site = 20

        data = []
        for site in range(n_sites):
            site_effect = np.random.normal(0, 0.5)
            for tree in range(n_trees_per_site):
                dbh = np.random.uniform(10, 50)
                height = 2 + 0.8 * np.log(dbh) + site_effect + np.random.normal(0, 0.2)
                data.append({"site": site, "dbh": dbh, "height": height})

        return pd.DataFrame(data)

    def test_initialization(self, hierarchical_data):
        """Test model initialization."""
        model = RandomInterceptModel(
            formula="height ~ dbh",
            group_var="site",
            data=hierarchical_data,
        )

        assert model.formula == "height ~ dbh"
        assert model.group_var == "site"

    def test_fit(self, hierarchical_data):
        """Test fitting random intercept model."""
        model = RandomInterceptModel(
            formula="height ~ np.log(dbh)",
            group_var="site",
            data=hierarchical_data,
        )

        result = model.fit()

        assert isinstance(result, MixedFitResult)
        assert result.n_obs == len(hierarchical_data)

    def test_predict(self, hierarchical_data):
        """Test prediction with fitted model."""
        model = RandomInterceptModel(
            formula="height ~ np.log(dbh)",
            group_var="site",
            data=hierarchical_data,
        )

        result = model.fit()

        test_data = pd.DataFrame({"dbh": [20, 30, 40]})
        predictions = model.predict(test_data)

        assert isinstance(predictions, np.ndarray)
        assert len(predictions) == 3

    def test_unfitted_model_predict_raises(self, hierarchical_data):
        """Test that prediction on unfitted model raises error."""
        model = RandomInterceptModel(
            formula="height ~ dbh",
            group_var="site",
            data=hierarchical_data,
        )

        test_data = pd.DataFrame({"dbh": [20, 30, 40]})

        with pytest.raises(ValueError, match="Model must be fitted"):
            model.predict(test_data)

    def test_unfitted_model_summary_raises(self, hierarchical_data):
        """Test that summary on unfitted model raises error."""
        model = RandomInterceptModel(
            formula="height ~ dbh",
            group_var="site",
            data=hierarchical_data,
        )

        with pytest.raises(ValueError, match="Model must be fitted"):
            model.summary()


class TestMixedFitResult:
    """Tests for MixedFitResult class."""

    @pytest.fixture
    def fitted_model(self):
        """Create a fitted model for testing."""
        np.random.seed(42)
        n_sites = 3
        n_trees_per_site = 15

        data = []
        for site in range(n_sites):
            site_effect = np.random.normal(0, 0.3)
            for tree in range(n_trees_per_site):
                dbh = np.random.uniform(10, 50)
                height = 2 + 0.8 * np.log(dbh) + site_effect + np.random.normal(0, 0.15)
                data.append({"site": site, "dbh": dbh, "height": height})

        df = pd.DataFrame(data)

        model = MixedEffectsModel(
            formula="height ~ np.log(dbh)",
            random_effects=["site"],
            data=df,
        )

        return model.fit()

    def test_params_attribute(self, fitted_model):
        """Test params attribute exists and is dict-like."""
        assert hasattr(fitted_model, "params")
        assert isinstance(fitted_model.params, dict)

    def test_std_errors_attribute(self, fitted_model):
        """Test std_errors attribute exists and is dict-like."""
        assert hasattr(fitted_model, "std_errors")
        assert isinstance(fitted_model.std_errors, dict)

    def test_variance_components_attribute(self, fitted_model):
        """Test variance_components attribute exists."""
        assert hasattr(fitted_model, "variance_components")
        assert isinstance(fitted_model.variance_components, dict)
        assert len(fitted_model.variance_components) > 0

    def test_random_effects_attribute(self, fitted_model):
        """Test random_effects attribute exists."""
        assert hasattr(fitted_model, "random_effects")
        assert isinstance(fitted_model.random_effects, list)
        assert len(fitted_model.random_effects) > 0

    def test_groups_attribute(self, fitted_model):
        """Test groups attribute exists."""
        assert hasattr(fitted_model, "groups")
        assert isinstance(fitted_model.groups, list)

    def test_predict_method(self, fitted_model):
        """Test predict method returns correct shape."""
        test_data = pd.DataFrame({"dbh": [20, 30, 40, 50, 60]})
        predictions = fitted_model.predict(test_data)

        assert isinstance(predictions, np.ndarray)
        assert len(predictions) == 5

    def test_predict_with_output_unit(self, fitted_model):
        """Test predict with output unit conversion."""
        test_data = pd.DataFrame({"dbh": [20, 30, 40]})

        # Should work even without units (returns dimensionless)
        predictions = fitted_model.predict(test_data, output_unit="meter")

        assert isinstance(predictions, np.ndarray)
        assert len(predictions) == 3
