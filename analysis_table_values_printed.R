library(plm) ## for the pooled OLS model
library(lmtest)
library(Hmisc)
library(ggplot2)
library(reticulate)
library(dplyr)
library(ggcorrplot) ## for corr plots w/ labels
library(car) ## to test for multicollinearity

#getwd()
#setwd() 

pd <- import("pandas")
df <- pd$read_pickle("result_df.pkl") #pickle data


## Data type conversions (data cleaning)
# Rename Year-Month column
colnames(df) <- gsub("-", ".", colnames(df))

# Df conversions
df <- df %>%
  mutate(Year.Month = as.Date(unlist(Year.Month), format = "%Y-%m-%d")) %>%
  subset(select=-c(no_count, total_count)) %>%
  rename_with(~"Underreporting", Total_prop_no) %>% 
  arrange(Borough, Year.Month)

# Convert necessary columns to numeric or factor
df$num_crimes <- as.numeric(df$num_crimes)
df$Underreporting <- as.numeric(df$Underreporting)
df$Contact.ward.officer <-as.numeric(df$Contact.ward.officer)
df$Informed.local <- as.numeric(df$Informed.local)
df$Listen.to.concerns <- as.numeric(df$Listen.to.concerns)
df$Relied.on.to.be.there <- as.numeric(df$Relied.on.to.be.there)
df$Treat.everyone.fairly <- as.numeric(df$Treat.everyone.fairly)
df$Trust.MPS <- as.numeric(df$Trust.MPS)
df$Understand.issues <- as.numeric(df$Understand.issues)
df$Good.job.local <- as.numeric(df$Good.job.local)


## Descriptive statistics and a correlation matrix
# Summary statistics
summary(df)
#Basic var info
describe(df)

# Correlation matrix
numeric_columns <- df %>% select_if(is.numeric)
cor_matrix <- cor(numeric_columns, use = "complete.obs")
ggcorrplot(cor_matrix, method = "circle", lab = TRUE)




### ORGANIZE PANEL DATA
# Cross-sectional time-series data; multiple entities (boroughs) 
# over multiple time periods (quarters)
pdata <- pdata.frame(df, index = c("Borough", "Year.Month"))



## CHECK MULTICOLLINEARITY AND POSSIBLY REMOVE SOME VARIABLES
# No multicollinearity, keep everything (hoorayyy)
testmodel <- lm(Trust.MPS ~ ., data=pdata)
ld.vars <- attributes(alias(testmodel)$Complete)$dimnames[[1]]
vif(testmodel)


## Perform the F-Test to compare Pooled OLS and LSDV
# H0: no individual (e.g. Borough) effects  
# HA: there are significant individual effects  
F_test_fixed <- function(pdata, pooled_model, LSDV_model){
  ## Pooled OLS model
  summary_pooling <- summary(pooled_model)
  R2_pooled <- summary_pooling$r.square
  print(summary_pooling)
  
  ## LSDV w/ dummy var
  # examine fixed group effects by introducing group (borough) dummy var
  summary_LSDV <- summary(LSDV_model)
  R2_LSDV <- summary_LSDV$r.square
  print(summary_LSDV)
  
  # F-test formula
  nT <- nrow(pdata)  # num observations
  n <- length(unique(pdata$Borough))  # num Boroughs
  k <- ncol(pdata) - 1  # num predictors
  print(nT)
  print(n)
  print(k)
  
  F_stat <- ((R2_LSDV - R2_pooled) / (n-1)) / ((1 - R2_LSDV) / (nT-n-k))
  print(paste("F-stat:", F_stat)) 
  print(paste("p-value:", pf(F_stat, n-1, nT-n-k)))
  return(pf(F_stat, n-1, nT-n-k) <= 0.05)
}

### CHOOSE PROPER PANEL DATA MODELS
## PANEL DATA MODELS examine group individual-specific effects and/or 

## time effects for heterogeneity or unobserved individual effects

## FE model: if intercepts vary across group/time period
  ## tested by F-test (based on the loss of goodness-of-fit)
    ## contrasts LSDV (robust) with pooled OLS (efficient)
    ## examines change in SSE and R2
    ## H0: all dummy par except for one for the dropped are all zero
    ## HA: at least one dummy par is not zero
    ## reject H0: there is a significant FE/increase in goodness-of-fit in 
                                        ## FE model (preferred over pooled OLS)
  ## LSDV uses dummy var, "within" does not
    ## "within": wipes out time-invariant var that don't vary within an entity
    ## "within": wrong R2 due to suppressed intercept
  ## "between" fits w/ individual/time means of (in)dependent var w/o dummies


## RE model: differences in error variance components across group/time period
  ## tested by LM test (Breusch and Pagan) 
    ## examines if individual/time specific variance components are zero
    ## H0: var_u = 0
    ## reject H0: there is a significant RE in panel data; RE model better deals
                                          ## w/ heterogeneity than pooled OLS


## Pooled OLS: if an individual effect u=0, OLS is efficient and consistent
  ## preferred if both FE/RE test H0 is NOT rejected


## Wu-Hausman test compares RE model to FE model similarity
  ## which effect more relevant/significant in panel data
  ## H0: individual effects are uncorrelated with model regressors
  ## reject H0: RE over FE
  ## H0 of no corr not violated, LSDV and GLS consistent, LSDV inefficient
  ## - else LSDV consistent but GLS inconsistent and biased
  ## intercept and dummy var must be excluded in computation

  ## on model that performs best, try one-way (1 var) and two-way effect 
  ##(2 dummies for individual and/or time var 
  ## - issues with estimation and interpretation)

####################### TRUST

## MODELS/TESTS
# We want to see what the determinants of "Trust.MPS" are.

# Create formula (PAS w/o good job local as that's confidence)
trust_predictors <- c("num_crimes", "Underreporting", "Contact.ward.officer", 
                "Informed.local", "Listen.to.concerns", "Relied.on.to.be.there", 
                "Treat.everyone.fairly", "Understand.issues")

trust_formula_str <- paste("Trust.MPS ~", paste(trust_predictors, 
                                                collapse = " + "))
trust_formula <- as.formula(trust_formula_str)

dummy_formula <- Trust.MPS ~ num_crimes + Underreporting + Contact.ward.officer + 
  Informed.local + Listen.to.concerns + Relied.on.to.be.there + 
  Treat.everyone.fairly + Understand.issues + factor(Borough)


## Pooled OLS model 
# R2 of 0.73955: model accounts for 74% of total variance in trust
trust_pooling_model <- plm(trust_formula, data = pdata, model = "pooling")

## LSDV w/ dummy var
# R2 of 0.8213; lower F-stat/DF as Pooled OLS; same p-val
trust_LSDV_model <- lm(formula = dummy_formula, data = pdata)

trust_f_test <- F_test_fixed(pdata, trust_pooling_model, trust_LSDV_model)
trust_f_test
# We see that the p-value is greater than 0.05.
# We fail to reject H0; Pooled OLS is sufficient


## POOLED OLS MODEL DECISIONS
## Determining best Pooled OLS model to account for time/borough effects
pooled_baseline <- plm(trust_formula, data = pdata, model = "pooling")
pooled_borough <- plm(update(trust_formula, reformulate(c(".", "Borough"))) 
pooled_time <- plm(update(trust_formula, reformulate(c(".", "Year.Month")))
                   , data = pdata, model = "pooling")
pooled_tb <- plm(update(trust_formula, reformulate(c(".", "Year.Month + Borough")))
                 , data = pdata, model = "pooling") 

# Compare baseline models to those that take (some) effects into account
sprintf("Fixed individual/borough effect: %s", pFtest(pooled_borough, pooled_baseline)$p.value <= 0.05) 
print(pFtest(pooled_borough, pooled_baseline))
sprintf("Fixed time effect: %s", pFtest(pooled_time, pooled_baseline)$p.value <= 0.05) 
print(pFtest(pooled_time, pooled_baseline))
sprintf("Fixed mixed effect: %s", pFtest(pooled_tb, pooled_baseline)$p.value <= 0.05) 
print(pFtest(pooled_tb, pooled_baseline))
# including FE for individual boroughs significantly improves the model
# including both FE for time and individual boroughs significantly improves model

## Test presence of random individual (borough) and time effects (Breusch-Pagan)
sprintf("Random individual effect: %s", plmtest(pooled_baseline, type="bp", 
                                                effect="individual")$p.value <= 0.05) 
print(plmtest(pooled_baseline, type="bp", 
              effect="individual")$p.value)
sprintf("Random time effect: %s", plmtest(pooled_baseline, type="bp", 
                                          effect="time")$p.value<= 0.05) 
print(plmtest(pooled_baseline, type="bp", 
              effect="time")$p.value)
sprintf("Random mixed effect: %s", plmtest(pooled_baseline, type="ghm", 
                                           effect="twoways")$p.value<= 0.05)  
print(plmtest(pooled_baseline, type="ghm", 
              effect="twoways")$p.value)
# significant RE associated with individual boroughs, should be considered
# significant RE associated with both individual boroughs and time periods



## Random effects model -> control unobserved time-invariant heterogeneity
# and assume that unobserved effects are uncorrelated w/ explanatory variables
## Use FE model to see whether effect twoways/individual works best

rand_ind_model <- plm(trust_formula, data = pdata, model = "random", 
                      effect = "individual", random.method = "walhus")
fixed_ind_model <- plm(trust_formula, data = pdata, model = "within", 
                       effect = "individual")
## Hausman test between fixed and random individual effects
# reject H0: FE model better than RE model for individual effects
hausman_test_ind <- phtest(fixed_ind_model, rand_ind_model)
print(hausman_test_ind)


rand_mixed_model <- plm(trust_formula, data = pdata, model = "random", 
                        effect = "twoways", random.method = "walhus")
fixed_mixed_model <- plm(trust_formula, data = pdata, model = "within", 
                         effect = "twoways")
## Hausman test between fixed and random twoways effects
# reject H0: FE model better than RE model for two-way effects
hausman_test_twoways <- phtest(fixed_mixed_model, rand_mixed_model)
print(hausman_test_twoways)



## Fixed effects model -> control unobserved time-invariant heterogeneity
# There are significant individual/Borough effects on trust and goodness-of-fit. 
# Preferred over pooled OLS model
summary(fixed_ind_model)
summary(fixed_mixed_model)

# Compare R-squared values
r2_fixed_ind <- summary(fixed_ind_model)$r.squared
r2_fixed_mixed <- summary(fixed_mixed_model)$r.squared

print(paste("R-squared (individual effects):", r2_fixed_ind))
print(paste("R-squared (two-way effects):", r2_fixed_mixed))


### CONCLUSION FOR FINAL MODEL FOR TRUST:
## FE INDIVIDUAL
# FE individual effects has a higher R2 -> better fit, 
# explains more of variance in trust


## If you are more concerned with capturing variability across individual entities 
#- (boroughs), the individual effects model is preferable.
## If you are also interested in capturing variability over time, the two-way 
#- effects model might be considered despite its lower R-squared value.

## ==> FE model with twoway or individual effects
summary(fixed_ind_model)


## CHECK AUTOCORRELATION
# H0: no autocorrelation -> p < 0.05, reject H0, we have serial correlation
pbgtest(fixed_ind_model)

## CHECK HOMOSCEDASTICITY
# H0: there is homoscedasticity -> p < 0.05, reject H0, we have heteroskedasticity
bptest(trust_formula, data=pdata, studentize=F)


# ==> to mitigate both of these problems, we can use robust standard errors to
# - ensure a correct output despite heteroskedaticity.
coeftest(fixed_ind_model, vcovHC(fixed_ind_model, method="arellano"))




####################### CONFIDENCE

## MODELS/TESTS
# We check what the determinants for Confidence = "Good.job.local" are

# Create formula (PAS w/o good job local as that's confidence)
conf_predictors <- c("num_crimes", "Underreporting", "Contact.ward.officer", 
                "Informed.local", "Listen.to.concerns", "Relied.on.to.be.there", 
                "Treat.everyone.fairly", "Understand.issues")

conf_formula_str <- paste("Good.job.local ~", paste(conf_predictors, 
                                                collapse = " + "))
conf_formula <- as.formula(conf_formula_str)

conf_dummy_formula <- Good.job.local ~ num_crimes + Underreporting + 
  Contact.ward.officer + Informed.local + Listen.to.concerns + 
  Relied.on.to.be.there + Treat.everyone.fairly + Understand.issues + 
  factor(Borough)


## Perform the F-Test to compare Pooled OLS and LSDV
# H0: no individual (e.g. Borough) effects
# HA: there are significant individual effects

## Pooled OLS model
conf_pooling_model <- plm(conf_formula, data = pdata, 
                                model = "pooling")

## LSDV w/ dummy var
conf_LSDV_model <- lm(formula = conf_dummy_formula, data = pdata)

conf_f_test <- F_test_fixed(pdata, conf_pooling_model, conf_LSDV_model)
conf_f_test
# We see that the p-value is greater than 0.05.
# We fail to reject H0; Pooled OLS is sufficient


## POOLED OLS MODEL DECISIONS
## Determining best Pooled OLS model to account for time/borough effects
cpooled_baseline <- plm(conf_formula, data = pdata, model = "pooling")
cpooled_borough <- plm(update(conf_formula, reformulate(c(".", "Borough"))), 
                      data = pdata, model = "pooling")
cpooled_time <- plm(update(conf_formula, reformulate(c(".", "Year.Month"))), 
                   data = pdata, model = "pooling")
cpooled_tb <- plm(update(conf_formula, reformulate(c(".", "Year.Month + Borough"))), 
                 data = pdata, model = "pooling")


# Compare baseline models to those that take (some) effects into account
sprintf("Fixed individual/borough effect: %s", 
        pFtest(cpooled_borough, cpooled_baseline)$p.value <= 0.05) 
print(pFtest(cpooled_borough, cpooled_baseline))
sprintf("Fixed time effect: %s", pFtest(cpooled_time, cpooled_baseline)$p.value <= 0.05) 
print(pFtest(cpooled_time, cpooled_baseline))
sprintf("Fixed mixed effect: %s", pFtest(cpooled_tb, cpooled_baseline)$p.value <= 0.05) 
print(pFtest(cpooled_tb, cpooled_baseline))
# including FE for individual boroughs significantly improves the model
# including FE for time effects significantly improves the model
# including both FE for time and individual boroughs significantly improves model

## Test presence of random individual (borough) and time effects (Breush-Pagan)
sprintf("Random individual effect: %s", plmtest(cpooled_baseline, type="bp",                                               effect="individual")$p.value <= 0.05) 
print(plmtest(cpooled_baseline, type="bp", effect="individual")) 

sprintf("Random time effect: %s", plmtest(cpooled_baseline, type="bp", 
                                          effect="time")$p.value<= 0.05) 
print(plmtest(cpooled_baseline , type="bp" , effect="time")) 

sprintf("Random mixed effect: %s", plmtest(cpooled_baseline, type="ghm", 
                                           effect="twoways")$p.value<= 0.05) 
print(plmtest(cpooled_baseline, type="ghm", effect="twoways"))
# significant RE associated with individual boroughs, should be considered
# significant RE associated with time periods, should be considered
# significant RE associated with both individual boroughs and time periods


## Random effects model -> control unobserved time-invariant heterogeneity
# and assume that unobserved effects are uncorrelated w/ explanatory variables
## Use FE model to see whether effect twoways/individual/both works best

crand_ind_model <- plm(conf_formula, data = pdata, model = "random", 
                      effect = "individual", random.method = "walhus")
cfixed_ind_model <- plm(conf_formula, data = pdata, model = "within", 
                        effect = "individual")
## Hausman test between fixed and random individual effects
# FE model better than RE model for individual effects
chausman_test_ind <- phtest(cfixed_ind_model, crand_ind_model)
print(chausman_test_ind)


crand_time_model <- plm(conf_formula, data = pdata, model = "random", 
                       effect = "time", random.method = "walhus")
cfixed_time_model <- plm(conf_formula, data = pdata, model = "within", 
                    effect = "time")
## Hausman test between fixed and random individual effects
# FE model better than RE model for individual effects
chausman_test_time <- phtest(cfixed_time_model, crand_time_model)
print(chausman_test_time)


crand_mixed_model <- plm(conf_formula, data = pdata, model = "random", 
                        effect = "twoways", random.method = "walhus")
cfixed_mixed_model <- plm(conf_formula, data = pdata, model = "within", 
                    effect = "twoways")
## Hausman test between fixed and random twoways effects
# FE model better than RE model for two-way effects
chausman_test_twoways <- phtest(cfixed_mixed_model, crand_mixed_model)
print(chausman_test_twoways)


## Fixed effects model -> control unobserved time-invariant heterogeneity
summary(cfixed_ind_model)
summary(cfixed_time_model)
summary(cfixed_mixed_model)

# Compare R-squared values
r2_cfixed_ind <- summary(cfixed_ind_model)$r.squared
r2_cfixed_time <- summary(cfixed_time_model)$r.squared
r2_cfixed_mixed <- summary(cfixed_mixed_model)$r.squared

print(paste("R-squared (individual effects):", r2_cfixed_ind))
print(paste("R-squared (time effects):", r2_cfixed_time))
print(paste("R-squared (two-way effects):", r2_cfixed_mixed))
## Model acc for time effects has the highest R2 values, therefore preferred
## Model acc for ind effects a close second
## Model acc for both performs very poorly in terms of R2 -> 0.23 and 0.15


### CONCLUSION ON FINAL MODEL FOR CONFIDENCE
summary(cfixed_ind_model)

## CHECK AUTOCORRELATION
# H0: no autocorrelation -> p < 0.05, reject H0, we have serial correlation
pbgtest(cfixed_ind_model)

## CHECK HOMOSCEDASTICITY
# H0: there is homoscedasticity -> p < 0.05, reject H0, we have heteroskedasticity
bptest(conf_formula, data=pdata, studentize=F)


# ==> to mitigate both of these problems, we can use robust standard errors to
# - ensure a correct output despite heteroskedaticity.
coeftest(cfixed_ind_model, vcovHC(cfixed_ind_model, method="arellano"))






####################### UNDERREPORTING


## MODELS/TESTS
# We check what the determinants for Underreporting are

# Create formula (PAS w/o good job local as that's confidence)
under_predictors <- c("num_crimes", "Good.job.local", "Trust.MPS", "Contact.ward.officer", 
                     "Informed.local", "Listen.to.concerns", "Relied.on.to.be.there", 
                     "Treat.everyone.fairly", "Understand.issues")

under_formula_str <- paste("Underreporting ~", paste(under_predictors, 
                                                    collapse = " + "))
under_formula <- as.formula(under_formula_str)

under_dummy_formula <- Underreporting ~ num_crimes + Good.job.local + Trust.MPS +
  Contact.ward.officer + Informed.local + Listen.to.concerns + 
  Relied.on.to.be.there + Treat.everyone.fairly + Understand.issues + 
  factor(Borough)


## Perform the F-Test to compare Pooled OLS and LSDV
# H0: no individual (e.g. Borough) effects
# HA: there are significant individual effects

## Pooled OLS model
under_pooling_model <- plm(under_formula, data = pdata, 
                          model = "pooling")

## LSDV w/ dummy var
under_LSDV_model <- lm(formula = under_dummy_formula, data = pdata)

under_f_test <- F_test_fixed(pdata, under_pooling_model, under_LSDV_model)
under_f_test 

# We see that the p-value is greater than 0.05.
# We fail to reject H0; Pooled OLS is sufficient



## POOLED OLS MODEL DECISIONS
## Determining best Pooled OLS model to account for time/borough effects
upooled_baseline <- plm(under_formula, data = pdata, model = "pooling")

upooled_borough <- plm(update(under_formula,reformulate(c(".", "Borough"))), 
                       data = pdata,model="pooling") 

upooled_time <- plm(update(under_formula, reformulate(c(".", "Year.Month"))), 
                    data = pdata, model = "pooling") 

upooled_tb <- plm(update(under_formula, reformulate(c(".", "Year.Month + Borough"))), 
                  data = pdata, model = "pooling")


# Compare baseline models to those that take (some) effects into account
sprintf("Fixed individual/borough effect: %s", pFtest(upooled_borough, upooled_baseline)$p.value <= 0.05) 
print(pFtest(upooled_borough, upooled_baseline))  

sprintf("Fixed time effect: %s", pFtest(upooled_time, upooled_baseline)$p.value <= 0.05) 
print(pFtest(upooled_time, upooled_baseline)) 

sprintf("Fixed mixed effect: %s", pFtest(upooled_tb, upooled_baseline)$p.value <= 0.05) 
print(pFtest(upooled_tb, upooled_baseline))
# including FE for individual boroughs significantly improves the model
# including FE for time effects significantly improves the model
# including both FE for time and individual boroughs significantly improves model

## Test presence of random individual (borough) and time effects (Breush-Pagan)
sprintf("Random individual effect: %s", plmtest(upooled_baseline, type="bp", 
                                                effect="individual")$p.value <= 0.05)  
print(plmtest(upooled_baseline, type="bp", effect="individual")$p.value) 

sprintf("Random time effect: %s", plmtest(upooled_baseline, type="bp", 
                                          effect="time")$p.value<= 0.05) 
print(plmtest(upooled_baseline, type="bp", effect="time")$p.value) 

sprintf("Random mixed effect: %s", plmtest(upooled_baseline, type="ghm", 
                                           effect="twoways")$p.value<= 0.05)  
print(plmtest(upooled_baseline, type="ghm", effect="twoways")$p.value) 

# significant RE associated with individual boroughs, should be considered
# significant RE associated with time periods, should be considered
# significant RE associated with both individual boroughs and time periods


## Random effects model -> control unobserved time-invariant heterogeneity
# and assume that unobserved effects are uncorrelated w/ explanatory variables
## Use FE model to see whether effect twoways/individual/both works best

urand_ind_model <- plm(under_formula, data = pdata, model = "random", 
                       effect = "individual", random.method = "walhus")
ufixed_ind_model <- plm(under_formula, data = pdata, model = "within", 
                        effect = "individual")
## IND: p-val <= 0.05, reject H0; FE model better for individual effects
uhausman_test_ind <- phtest(ufixed_ind_model, urand_ind_model)
print(uhausman_test_ind)


urand_time_model <- plm(under_formula, data = pdata, model = "random", 
                        effect = "time", random.method = "walhus")
ufixed_time_model <- plm(under_formula, data = pdata, model = "within", 
                         effect = "time")
# TIME: Fail to reject H0; no significant time effects; RE over FE
uhausman_test_time <- phtest(ufixed_time_model, urand_time_model)
print(uhausman_test_time)


urand_mixed_model <- plm(under_formula, data = pdata, model = "random", 
                         effect = "twoways", random.method = "walhus")
ufixed_mixed_model <- plm(under_formula, data = pdata, model = "within", 
                          effect = "twoways")
# BOTH: Fail to reject H0; no significant time effects; RE over FE
uhausman_test_twoways <- phtest(ufixed_mixed_model, urand_mixed_model)
print(uhausman_test_twoways)

## TIME, BOTH: RE model for time and two-way effects is consistent
## IND: use FE model for individual effects
## => if individual effects are more critical in the analysis 
## - (significant differences across boroughs), use FE
## => individual heterogeneity is crucial for the analysis, we use FE ind


## Fixed effects model -> control unobserved time-invariant heterogeneity
summary(ufixed_ind_model)

# Compare R-squared values
r2_ufixed_ind <- summary(ufixed_ind_model)$r.squared
print(paste("R-squared (fixed individual effects):", r2_ufixed_ind)) 

r2_urand_time <- summary(urand_time_model)$r.squared
print(paste("R-squared (random time effects):", r2_urand_time)) 

r2_urand_mixed <- summary(urand_mixed_model)$r.squared
print(paste("R-squared (random mixed effects):", r2_urand_mixed))



### CONCLUSION ON FINAL MODEL FOR UNDERREPORTING
summary(ufixed_ind_model)
# R2 very low (0.15 and 0.09). Small proportion of variance of under-reporting 
# - is explained by the independent variables
# there are other factors not included in the model that could be influencing
  ## future work?
  ## add non-linear terms?
  ## In some fields (social sciences) low R2 are common; human behavior 
  ## - influenced by a wide range of factors, many of which difficult to measure.



## CHECK AUTOCORRELATION
# H0: no autocorrelation -> p < 0.05, reject H0, we have serial correlation
pbgtest(ufixed_ind_model) 

## CHECK HOMOSCEDASTICITY
# H0: there is homoscedasticity -> p < 0.05, reject H0, we have heteroskedasticity
bptest(under_formula, data=pdata, studentize=F) 




# ACF plot for residuals 
residuals_under_reporting <- residuals(ufixed_ind_model)
acf(residuals_under_reporting, main = "Autocorrelation Function (ACF) of Residuals for Under-reporting")
# PACF plot for residuals
pacf(residuals_under_reporting, main = "Partial Autocorrelation Function (PACF) of Residuals for Under-reporting")

### AUTOCORRELATION AND HOMOSKEDASTICITY FOR . . .  

## Trust  
pbgtest(fixed_ind_model) # reject H0
bptest(fixed_ind_model, data=pdata, studentize=F) #reject H0 
# ACF plot for residuals 
residuals_trust <- residuals(fixed_ind_model)
acf(residuals_trust, main = "Autocorrelation Function (ACF) of Residuals for Trust")
# PACF plot for residuals
pacf(residuals_trust, main = "Partial Autocorrelation Function (PACF) of Residuals for Trust")

## Confidence 
pbgtest(cfixed_ind_model) # reject H0
bptest(cfixed_ind_model, data=pdata, studentize=F) # reject H0 
# ACF plot for residuals 
residuals_confidence <- residuals(cfixed_ind_model)
acf(residuals_confidence, main = "Autocorrelation Function (ACF) of Residuals for Confidence")
# PACF plot for residuals
pacf(residuals_confidence, main = "Partial Autocorrelation Function (PACF) of Residuals for Confidence")

# ==> to mitigate both of these problems, we can use robust standard errors to
# - ensure a correct output despite heteroskedasticity and autocorrelation.
# This bypasses these problems but makes your results robust and reliable.
coeftest(ufixed_ind_model, vcovHC(ufixed_ind_model, method="arellano"))

################################################################################

## FINAL MODELS > MODELS WITH ROBUST SE
# Fixed Individual Effect TRUST model
coeftest(fixed_ind_model, vcovHC(fixed_ind_model, method="arellano"))
# Fixed Individual Effect CONFIDENCE model
coeftest(cfixed_ind_model, vcovHC(cfixed_ind_model, method="arellano"))
# Fixed Individual Effect UNDERREPORTING model
coeftest(ufixed_ind_model, vcovHC(ufixed_ind_model, method="arellano")) 

## Getting the r squared 
# summary(fixed_ind_model) 
# summary(cfixed_ind_model) 
# summary(ufixed_ind_model)

## MODELS WITHOUT ROBUST SE
# Fixed Individual Effect TRUST model
coeftest(fixed_ind_model)
# Fixed Individual Effect CONFIDENCE model
coeftest(cfixed_ind_model)
# Fixed Individual Effect UNDERREPORTING model
coeftest(ufixed_ind_model)

