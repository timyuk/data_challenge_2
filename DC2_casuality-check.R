library(plm) ## for the pooled OLS model
library(lmtest)
library(ggplot2)
library(reticulate)
library(dplyr)
library(corrplot) ## for corr plots
library(ggcorrplot) ## for corr plots w/ labels

pd <- import("pandas")
df <- pd$read_pickle("C:/Users/20223084/Documents/data_challenge_2/result_df.pkl") #pickle data

df

## Data type conversions (data cleaning)
# Rename Year-Month column
colnames(df) <- gsub("-", ".", colnames(df))

# Convert Year-Month to Date type
df <- df %>%
  mutate(Year.Month = as.Date(unlist(Year.Month), format = "%Y-%m-%d"))


### CHECK TRUST AND REPORTING
### CHOOSE BOROUGHS w/ UNDERREPORTING AND CRIME PER CAPITA


# Convert necessary columns to numeric
df$num_crimes <- as.numeric(df$num_crimes)
df$Total_prop_no <- as.numeric(df$Total_prop_no)
df$no_count <- as.numeric(df$no_count)
df$total_count <- as.numeric(df$total_count)
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

# Correlation matrix
numeric_columns <- df %>% select_if(is.numeric)
cor_matrix <- cor(numeric_columns, use = "complete.obs")

# # Visualize the correlation matrix using corrplot
# corrplot(cor_matrix, method = "circle")

# Visualize the correlation matrix using ggcorrplot
ggcorrplot(cor_matrix, method = "circle", lab = TRUE)


## Convert to panel data with Borough and Year-Month as primary keys
## PANEL DATA: cross-sectional time-series data; multiple entities over multiple time periods
## Entities: crime, underreporting, PAS measures
## Time dimension: years/quarters
## Variables:
    # Time invariant: borough names
    # Time-varying: num_crimes, measure proportions, underreporting

# Convert Year.Month to character (needed for pdata.frame)
df$Year.Month <- as.character(df$Year.Month)

# Sort the dataframe by Borough and Year.Month
df <- df %>% arrange(Borough, Year.Month)

# Convert dataframe to pdata.frame
pdata <- pdata.frame(df, index = c("Borough", "Year.Month"))

# Convert Year.Month for time effects model
pdata$Year.Month <- as.numeric(pdata$Year.Month)


### MODELS/TESTS
# We want to see what the determinants of "Trust.MPS" are.
# We also need to check what the determinants for Confidence = "Good.job.local" are

# Create formula
predictors <- c("num_crimes", "no_count", "total_count", 
                "Good.job.local", "Contact.ward.officer", 
                "Informed.local", "Listen.to.concerns", 
                "Relied.on.to.be.there", "Treat.everyone.fairly", 
                "Total_prop_no", "Understand.issues")

formula_str <- paste("Trust.MPS ~", paste(predictors, collapse = " + "))
formula <- as.formula(formula_str)



## Regression for statistical significance -- just to see how it performs
# Fit a **linear** regression model
model <- lm(formula, data = pdata)
summary(model)


## Pooled OLS model
# Fit a pooled OLS model using plm
pooling_model <- plm(formula, data = pdata, model = "pooling")
summary(pooling_model)

# Fixed effects model -> control unobserved time-invariant heterogeneity
# i.e. Borough is used as an explanatory variable
fe_model <- plm(formula, data=pdata, model="within")
summary(fe_model)

# Random effects model -> control unobserved time-invariant heterogeneity
# and assume that unobserved effects are uncorrelated w/ explanatory variables
# i.e. num_crimes, no_count
re_model <- plm(formula, data=pdata, model="random")
summary(re_model)

# # Time effects model -> control for time-specific effects
# # Year.Month is converted to a numeric column to deal with this
# time_model <- plm(formula, data=pdata, model="time")
# summary(time_model)


## Perform Wu-Hausman test to compare fixed effects and random effects models
# H0: RE are consistent and efficient
# HA: FE are consistent and efficient
wu_hausman_test <- phtest(fe_model, re_model)
print(wu_hausman_test)

## We conclude RE model is inconsistent, FE model should be preferred.
## p-value is significant (< 0.05), so RE model is inconsistent with the data.
## There are unobserved time-invariant factors (individual effects) 
# influencing the outcome (Total_prop_no), which are not accounted for in the 
# random effects model but are captured by the fixed effects model.

## CHOSEN FE MODEL WITH TIME EFFECTS
# factor(Year.Month) included to capture time-specific effects.
# time dummies account for any systematic time trends or seasonality in data.
predictors2 <- c("num_crimes", "no_count", "total_count", 
                "Good.job.local", "Contact.ward.officer", 
                "Informed.local", "Listen.to.concerns", 
                "Relied.on.to.be.there", "Treat.everyone.fairly", 
                "Trust.MPS", "Understand.issues", factor("Year.Month"))

formula_str2 <- paste("Total_prop_no ~", paste(predictors2, collapse = " + "))
formula2 <- as.formula(formula_str2)

fe_fin_model <- plm(formula2, data=pdata, model="within")
summary(fe_fin_model)








