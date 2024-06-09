# imports  
# install.packages("readr")
# install.packages("reticulate")  
# install.packages("dplyr") 
# install.packages("ggplot2") 
# install.packages("plm") 
# install.packages("lmtest") 
# install.packages("corrplot")
library(ggplot2) ## plotting
library(readr) ## for loading csv files
library(reticulate) ## for loading .pkl files 
library(dplyr) ## operating on dataframes
library(plm) ## for the pooled OLS model
library(lmtest) ## for linear model 
library(corrplot) ## for corr plots 
library(stats) ## for autocorrelation plots


py_install("pandas") # from reticulate package
pandas <- import("pandas") # to load pandas to read pickle files

# Borough selection 

boroughs = c('Westminster', 'Kingston', 'Chelsea',  'Bexley', 'Richmond upon Thames')

# load data  
setwd("C:/Users/diego/OneDrive/Desktop/DC_2")
london_street <- pandas$read_csv('london_street')  
pas_detailed <- pandas$read_pickle("C:/Users/diego/OneDrive/Desktop/DC_2/pas_data_ward_level/pas_a/PAS_detailed.pkl")
pas_detailed2 <- pandas$read_pickle("C:/Users/diego/OneDrive/Desktop/DC_2/pas_data_ward_level/pas_a/PAS_detailed2.pkl")
pas_detailed_df <- as.data.frame(pas_detailed)
pas_detailed2_df <- as.data.frame(pas_detailed2) 
results <- pandas$read_pickle("C:/Users/diego/OneDrive/Desktop/DC_2/result_df.pkl") 
df_result <- as.data.frame(results)  


# Convert necessary columns to numeric
df_result$num_crimes <- as.numeric(df_result$num_crimes)
df_result$Total_prop_no <- as.numeric(df_result$Total_prop_no)
df_result$no_count <- as.numeric(df_result$no_count)
df_result$total_count <- as.numeric(df_result$total_count)
df_result$Contact.ward.officer <-as.numeric(df_result$Contact.ward.officer)
df_result$Informed.local <- as.numeric(df_result$Informed.local)
df_result$Listen.to.concerns <- as.numeric(df_result$Listen.to.concerns)
df_result$Relied.on.to.be.there <- as.numeric(df_result$Relied.on.to.be.there)
df_result$Treat.everyone.fairly <- as.numeric(df_result$Treat.everyone.fairly)
df_result$Trust.MPS <- as.numeric(df_result$Trust.MPS)
df_result$Understand.issues <- as.numeric(df_result$Understand.issues)
df_result$Good.job.local <- as.numeric(df_result$Good.job.local) 

# Altering scale of values to make coefficients more interpretable  
df_result$num_crimes <- 
df_result$Total_prop_no <- 
df_result$no_count <- 
df_result$total_count <- 
df_result$Contact.ward.officer <- df_result$Contact.ward.officer * 100
df_result$Informed.local <- df_result$Informed.local * 100
df_result$Listen.to.concerns <- df_result$Listen.to.concerns * 100
df_result$Relied.on.to.be.there <- df_result$Relied.on.to.be.there * 100
df_result$Treat.everyone.fairly <- df_result$Treat.everyone.fairly * 100
df_result$Trust.MPS <- df_result$Trust.MPS * 100
df_result$Understand.issues <- df_result$Understand.issues * 100
df_result$Good.job.local <- df_result$Good.job.local * 100

for (x in names(df_result)){  
  df_result$x <- df
}

# analyzing the time trend in trust measure 

ts_cols = c('Trust.MPS', 'Borough', 'Year-Month') # get relevant data
trust_ts = df_result[, ts_cols]  

# Plotting
global_trust_ts <- trust_ts %>% 
  group_by(`Year-Month`) %>%
  summarise(mean_Trust = mean(`Trust.MPS`, na.rm = TRUE)) # Calculate the mean Trust.MPS for each Year-Month

# Calculate ACF and PACF
trust_acf <- acf(global_trust_ts$mean_Trust, main = "ACF: Global Trust MPS")
trust_pacf <- pacf(global_trust_ts$mean_Trust, main = "PACF: Global Trust MPS") 

# Plot ACF 
dev.off()
plot(trust_acf, main = "ACF: Global Trust MPS")
# Plot PACF 
dev.off()
plot(trust_pacf, main = "PACF: Global Trust MPS")  

# Building the model 
# Create formula
predictors <- c("num_crimes", "no_count", "total_count", 
                "Good.job.local", "Contact.ward.officer", 
                "Informed.local", "Listen.to.concerns", 
                "Relied.on.to.be.there", "Treat.everyone.fairly", 
                "Total_prop_no", "Understand.issues") 

# Creating the global dataframe for the city of London 
# Group by col1 and then summarize the data
df_global <- df_result %>%
  group_by('Year-Month') %>%
  summarise(
    mean_num_crimes <- mean(num_crimes), 
    mean_total_prop_no <- mean(Total_prop_no), 
    mean_no_count <- mean(no_count) ,
    mean_total_count <- mean(total_count) ,
    mean_contact <- mean(Contact.ward.officer)  ,
    mean_informed <- mean(Informed.local) , 
    mean_listen <- mean(Listen.to.concerns) ,
    mean_relied <- mean(Relied.on.to.be.there) ,
    mean_fair <- mean(Treat.everyone.fairly) ,
    mean_mps <- mean(Trust.MPS) ,
    mean_issues <-mean(Understand.issues) ,
    mean_good_job <- mean(Good.job.local) 
  )

print(df_global)

# Global Trust 

formula_str <- paste("Trust.MPS ~", paste(predictors, collapse = " + "))
formula <- as.formula(formula_str)

# Fixed effects model and analyzing the residuals  

fe_model <- plm(formula, data=df_global, model="within")
summary(fe_model) 

fe_residuals <- residuals(fe_model) 
print(fe_residuals)  
dev.off()
plot(fe_residuals)

# calculating the autoregressive terms  

df_result_global <- df_result_global %>%
  mutate(lag_1 = lead(Trust.MPS, 1))
df_result <- df_result %>%
  mutate(lag_2 = lead(Trust.MPS, 2))
df_result <- df_result %>%
  mutate(lag_3 = lead(Trust.MPS, 3))
df_result <- df_result %>%
  mutate(lag_4 = lead(Trust.MPS, 4))


# checking global seasonality 

# calculating seasonality column 

# model with autoregressive terms 

# model with seasonality 

# best performing model

# creating local data  

df_westminster <- subset(df_result, Borough=='Westminster')
df_kingston <- subset(df_result, Borough=='Kingston')
df_chelsea <- subset(df_result, Borough=='Chelsea')
df_bexley <- subset(df_result, Borough=='Bexley')
df_richmond <- subset(df_result, Borough=='Richmond upon Thames')

# Model of Borough 1   

# Model of Borough 2 

# Model of Borough 3 

# Model of Borough 4  

# Model of Borough 5 

# analyzing the time trend in under-reporting measure 

# analyzing the time trend in crime measure 

# re-scaling for percentage change >>>> logs? 

