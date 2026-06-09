"""Mixed effects models for hierarchical forestry data.

This module provides classes and functions for fitting mixed effects models
using statsmodels. Mixed effects models are commonly used in forestry research
to account for hierarchical data structures (e.g., trees nested within plots
or sites).

Example:
    >>> from pylometree.fitting.mixed_effects import MixedEffectsModel
    >>> import pandas as pd
    >>> import numpy as np
    >>>
    >>> # Create sample data with hierarchical structure
    >>> np.random.seed(42)
    >>> n_sites = 5
    >>> n_plots_per_site = 4
    >>> n_trees_per_plot = 10
    >>>
    >>> data = []
    >>> for site in range(n_sites):
    ...     site_effect = np.random.normal(0, 0.5)
    ...     for plot in range(n_plots_per_site):
    ...         plot_effect = np.random.normal(0, 0.3)
    ...         for tree in range(n_trees_per_plot):
    ...             dbh = np.random.uniform(10, 50)
    ...             height = 2 + 0.8 * np.log(dbh) + site_effect + plot_effect + np.random.normal(0, 0.2)
    ...             data.append({'site': site, 'plot': plot, 'dbh': dbh, 'height': height})
    >>> df = pd.DataFrame(data)
    >>>
    >>> # Fit mixed effects model
    >>> model = MixedEffectsModel(
    ...     formula='height ~ np.log(dbh)',
    ...     random_effects=['site'],
    ...     data=df
    ... )
    >>> result = model.fit()
    >>> print(result.summary())
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import patsy
from statsmodels.api import MixedLM

from pylometree.units import Units, convert_units, set_units


@dataclass
class MixedFitResult:
    """Result of a mixed effects model fit.

    Extends FitResult with mixed effects specific attributes.
    """

    model_name: str
    formula: str
    params: Dict[str, float]
    std_errors: Dict[str, float]
    n_obs: int
    n_params: int
    df_resid: int
    df_model: int
    log_likelihood: Optional[float]
    aic: Optional[float]
    bic: Optional[float]
    r_squared: Optional[float]
    predictor_vars: List[str]
    response_var: str
    random_effects: List[str] = field(default_factory=list)
    variance_components: Dict[str, float] = field(default_factory=dict)
    groups: List[str] = field(default_factory=list)
    units: Dict[str, str] = field(default_factory=dict)
    _fitted_model: Any = field(default=None, repr=False)
    _data: Optional[pd.DataFrame] = field(default=None, repr=False)

    def predict(
        self, data: pd.DataFrame, output_unit: Optional[str] = None
    ) -> np.ndarray:
        """Predict response variable for new data.

        Args:
            data: DataFrame with predictor variables
            output_unit: Target unit for output (if units enabled)

        Returns:
            Predicted values as numpy array
        """
        # Use patsy to build design matrix from formula (handles transformations)
        # Extract just the RHS of the formula (predictors)
        formula_rhs = self.formula.split("~")[1].strip()
        
        # Build design matrix using patsy
        X = patsy.dmatrix(formula_rhs, data)
        
        # Get fixed effects parameters in correct order
        fe_params = [
            self.params[col]
            for col in self._fitted_model.exog_names
            if col in self.params
        ]
        params_array = np.array(fe_params)

        # Predict using matrix multiplication (statsmodels does same internally)
        pred = np.dot(X, params_array)

        # Convert units if specified
        if output_unit and self.units.get("response"):
            pred = convert_units(pred, self.units["response"], output_unit)

        return pred


class MixedEffectsModel:
    """Mixed effects model for hierarchical data.

    Provides a unified interface for fitting mixed effects models using
    statsmodels. Supports both continuous and generalized linear mixed models.

    Attributes:
        formula: Model formula (e.g., 'y ~ x1 + x2')
        random_effects: List of random effect grouping variables
        data: Training data
        family: GLM family for generalized models (optional)
        re_formula: Random effects formula (optional)
        vc_formula: Variance components formula (optional)
    """

    def __init__(
        self,
        formula: str,
        random_effects: List[str],
        data: pd.DataFrame,
        family: Optional[Any] = None,
        re_formula: Optional[str] = None,
        vc_formula: Optional[str] = None,
    ):
        """Initialize mixed effects model.

        Args:
            formula: Model formula (e.g., 'height ~ dbh')
            random_effects: List of random effect grouping variables
            data: Training data DataFrame
            family: GLM family for generalized models (optional)
            re_formula: Random effects formula (optional)
            vc_formula: Variance components formula (optional)
        """
        self.formula = formula
        self.random_effects = random_effects
        self.data = data.copy()
        self.family = family
        self.re_formula = re_formula
        self.vc_formula = vc_formula

        self.model: Optional[MixedLM] = None
        self.result: Optional[MixedFitResult] = None

    def fit(
        self,
        start_params: Optional[np.ndarray] = None,
        **kwargs,
    ) -> MixedFitResult:
        """Fit the mixed effects model.

        Args:
            start_params: Initial parameter values (optional)
            **kwargs: Additional arguments passed to MixedLM.fit

        Returns:
            MixedFitResult with fitted parameters and statistics
        """
        # Prepare data - drop rows with NaN
        data = self.data.dropna()

        # Build formula for statsmodels
        # statsmodels uses ~ for fixed effects, groups for random effects
        fixed_part = self.formula.split("~")[1].strip()
        mixed_formula = f"{self.formula.split('~')[0].strip()} ~ {fixed_part}"

        # Fit the model
        try:
            model = MixedLM.from_formula(
                mixed_formula,
                data,
                groups=data[self.random_effects[0]] if self.random_effects else None,
            )

            self.model = model
            result = model.fit(start_params=start_params, **kwargs)

            self.result = self._create_result(result, model, data)

            return self.result

        except Exception as e:
            raise RuntimeError(f"Failed to fit mixed effects model: {e}")

    def _create_result(
        self,
        result: Any,
        model: MixedLM,
        data: pd.DataFrame,
    ) -> MixedFitResult:
        """Create MixedFitResult from fitted model.

        Args:
            result: Fitted statsmodels MixedLMResults
            model: Fitted MixedLM model
            data: Training data

        Returns:
            MixedFitResult with model results
        """
        # Extract fixed effects
        fixed_effects = result.fe_params
        fixed_se = result.bse_fe

        # Extract variance components
        variance_components = {}
        if hasattr(result, "vcomp") and len(result.vcomp) > 0:
            variance_components = dict(result.vcomp)
        elif hasattr(result, "cov_re") and result.cov_re is not None:
            # cov_re may be a DataFrame or array
            if hasattr(result.cov_re, "iloc"):
                # DataFrame - get first element
                variance_components = {
                    "random_intercept": float(result.cov_re.iloc[0, 0])
                }
            elif hasattr(result.cov_re, "__getitem__"):
                try:
                    variance_components = {
                        "random_intercept": float(result.cov_re[0, 0])
                    }
                except (IndexError, KeyError, TypeError):
                    # Handle multi-index or other access patterns
                    variance_components = {
                        "random_intercept": float(result.cov_re.values[0, 0])
                    }

        # Get predictor and response variable names
        response_var = self.formula.split("~")[0].strip()
        # Extract actual column names from formula (remove function calls like np.log())
        predictor_vars_raw = self.formula.split("~")[1].strip().split("+")
        predictor_vars = []
        for pv in predictor_vars_raw:
            pv = pv.strip()
            # Extract column name from function calls like np.log(dbh) -> dbh
            if "(" in pv and ")" in pv:
                col_name = pv.split("(")[1].split(")")[0].strip()
                predictor_vars.append(col_name)
            else:
                predictor_vars.append(pv)

        # Handle NaN values from statsmodels
        llf = result.llf
        log_likelihood = float(llf) if llf is not None and not np.isnan(llf) else None
        aic_val = result.aic
        aic = float(aic_val) if aic_val is not None and not np.isnan(aic_val) else None
        bic_val = result.bic
        bic = float(bic_val) if bic_val is not None and not np.isnan(bic_val) else None

        # Create result object
        result_obj = MixedFitResult(
            model_name="mixed_effects",
            formula=self.formula,
            params=dict(fixed_effects),
            std_errors=dict(fixed_se),
            n_obs=int(result.nobs),
            n_params=len(fixed_effects),
            df_resid=int(result.df_resid),
            df_model=int(result.df_modelwc),
            log_likelihood=log_likelihood,
            aic=aic,
            bic=bic,
            r_squared=None,  # statsmodels MixedLM doesn't provide pseudo R2
            predictor_vars=predictor_vars,
            response_var=response_var,
            random_effects=self.random_effects,
            variance_components=variance_components,
            groups=self.random_effects,
            units={},
        )

        # Store reference to fitted model for prediction
        result_obj._fitted_model = model
        result_obj._data = data

        return result_obj

    def predict(
        self, data: pd.DataFrame, output_unit: Optional[str] = None
    ) -> np.ndarray:
        """Predict response variable for new data.

        Args:
            data: DataFrame with predictor variables
            output_unit: Target unit for output (if units enabled)

        Returns:
            Predicted values as numpy array
        """
        if self.result is None:
            raise ValueError("Model must be fitted before prediction")

        return self.result.predict(data, output_unit=output_unit)

    def summary(self) -> str:
        """Return model summary as string.

        Returns:
            Model summary string
        """
        if self.result is None:
            raise ValueError("Model must be fitted before generating summary")

        summary_lines = [
            "=" * 60,
            "Mixed Effects Model Summary",
            "=" * 60,
            f"Formula: {self.formula}",
            f"Random effects: {', '.join(self.random_effects)}",
            "",
            "Fixed Effects:",
            "-" * 40,
        ]

        for name, value in self.result.params.items():
            se = self.result.std_errors.get(name, 0)
            t_stat = value / se if se > 0 else 0
            summary_lines.append(
                f"  {name:20s} {value:12.6f} (SE: {se:12.6f}, t: {t_stat:8.2f})"
            )

        summary_lines.extend(
            [
                "",
                "Variance Components:",
                "-" * 40,
            ]
        )

        for name, value in self.result.variance_components.items():
            summary_lines.append(f"  {name:20s} {value:12.6f}")

        summary_lines.extend(
            [
                "",
                "Model Fit:",
                "-" * 40,
                f"  Observations:      {self.result.n_obs}",
                f"  Parameters:        {self.result.n_params}",
                f"  Residual df:       {self.result.df_resid}",
                f"  Model df:          {self.result.df_model}",
                f"  Log-likelihood:    {self.result.log_likelihood if self.result.log_likelihood is not None else 'N/A':>12}",
                f"  AIC:               {self.result.aic if self.result.aic is not None else 'N/A':>12}",
                f"  BIC:               {self.result.bic if self.result.bic is not None else 'N/A':>12}",
                f"  Pseudo R-squared:  {self.result.r_squared if self.result.r_squared is not None else 'N/A':>12}",
                "=" * 60,
            ]
        )

        return "\n".join(summary_lines)


class RandomInterceptModel:
    """Random intercept model for hierarchical data.

    Simplified interface for random intercept models where only
    intercepts vary by grouping variable.

    Example:
        >>> model = RandomInterceptModel(
        ...     formula='height ~ dbh',
        ...     group_var='site',
        ...     data=df
        ... )
        >>> result = model.fit()
    """

    def __init__(
        self,
        formula: str,
        group_var: str,
        data: pd.DataFrame,
    ):
        """Initialize random intercept model.

        Args:
            formula: Model formula (e.g., 'height ~ dbh')
            group_var: Grouping variable for random intercepts
            data: Training data DataFrame
        """
        self.formula = formula
        self.group_var = group_var
        self.data = data.copy()
        self.model: Optional[MixedEffectsModel] = None

    def fit(self, **kwargs) -> MixedFitResult:
        """Fit the random intercept model.

        Args:
            **kwargs: Arguments passed to MixedEffectsModel.fit

        Returns:
            MixedFitResult with fitted parameters
        """
        mixed_model = MixedEffectsModel(
            formula=self.formula,
            random_effects=[self.group_var],
            data=self.data,
        )

        self.model = mixed_model
        return mixed_model.fit(**kwargs)

    def predict(
        self, data: pd.DataFrame, output_unit: Optional[str] = None
    ) -> np.ndarray:
        """Predict response variable for new data.

        Args:
            data: DataFrame with predictor variables
            output_unit: Target unit for output (if units enabled)

        Returns:
            Predicted values as numpy array
        """
        if self.model is None:
            raise ValueError("Model must be fitted before prediction")

        return self.model.predict(data, output_unit=output_unit)

    def summary(self) -> str:
        """Return model summary as string.

        Returns:
            Model summary string
        """
        if self.model is None:
            raise ValueError("Model must be fitted before generating summary")

        return self.model.summary()
