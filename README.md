# Ride Hailing Service

This repository contains the code, analysis, and report on a project to identify the highest profit yielding pricing strategy for a new Ride Hailing Serivce, given some data from a similar service in the area.


## Problem:

A new ride hailing service is being launched that connects riders with drivers for trips between the Airport and Downtown. It’ll be active for only 12 months. The riders are charged a fixed rate of $30 per ride, and I have been tasked to propose a pricing strategy to maximise the profit of the business over the 12 months, given some contraints and assumptions. This document will present my strategy, as well as the thought process and data derived results behind it.


## Bottom Line Up Front: The Best Strategy

Given the contraints, assumptions, and data given by the client, the optimal pricing strategy is to pay a fixed rate of $25.75 per ride, resulting in a profit of $4.25 per ride assuming no other costs, and a total average profit across the 12 months of $50,994.39, with a 95% confidence interval of ($48,452.82, $52,770.18).


## Methods:

### The Model: Assumptions and Constraints

For each event the ride-hailing system connects one rider request with one driver. The rider is charged a flat $30, and the driver can be payed any amount, P. The profit per ride is calculated as ($30 - P).

The riders:
- There are a total of 10,000 riders in the city.
- The service begins with 0 riders active.
- Each month a maximum of 1,000 new riders can join the service and be eligible to request rides (become active).
- In the first month that a rider is active, they request an average of 1 ride per month (with the number of rides requested coming from a Poisson distribution).
- In each subsequent month, riders request rides based on a Poisson distribution where lambda is the number of rides that they found a *match* for in the previous month.
- If a rider finds no matches in a month (which may happen either because they request no rides or because they request rides and find no matches), they leave the service and never return.

The drivers:
- There are a practically unlimited supply of drivers available.
- When a ride is requested, a very large pool of drivers see the request and can choose whether to accept or reject it.
- A ride request is accepted with some probability q which is based on the rate of pay P for the ride (the acceptance is generated from a Bernoulli distribution).

The Data:
- Data was provided from a similar service denoting what the pay, P, was and whether the ride was accepted.
- From the exploratory analysis, there is a strong positive non-linear relationship between the probability of acceptance and the rate of pay. A logistic regression model was fit to the data to estimate the probability that a given rate of pay would be accepted.
- These estimated probabilities are used in the simulation.

The Model:
- The model is simulated in discrete time with 1-month units.
- The population of riders are considered homogeneous and exchangable, but with unique histories. 
- No features of the driver population are considered, just the probability of acceptance based on the data.
- The maximum number (1,000) of riders is assumed to be acquired each month, at the start of the month, so their rate of requests are that of a whole month.

### The Models

There is a clear trade off between the number of riders active (and the number of requests per rider) and the profit per ride. A higher rate of acceptance leads to more riders active and more ride requests, but lowers the profit per ride, or may even lead to a loss per ride. With this in mind I developed 3 different models to explore this relationship and identify if a non-uniform strategy could increase profits.

#### Flat Rate

In this model all of the drivers are payed at a fixed rate across for every ride across the whole 12 months. This will find the natural balance point between the rate of acceptance and the profit per ride.

#### Adaptive Rate

The system is set up such that a if a rider has no rides accepted during a month then they will leave the service and never return, and thus not generate any additional revenue. A portion of riders will naturally leave the service without any possible remedy if they make no requests in a month, but some will leave because their requests weren't accepted, and these cases are potentially avoidable. If an individual leaves in month 1 because their request wasn't accepted, then we are potentially missing out on 11 months of additional revenue, which is quite substantial.

This model works by attempting to maximise the number of riders who remain active, and then maximise profits on additional rides. If a rider has yet to have an accepted ride that month, the pay for their current request is at a premium (possibly even a loss) to maximise the probability of acceptance and guarantee they will stay active, any additional rides requested by this rider that month are payed at a value to optimise profit.

#### Bait and Switch Rate

As in the adaptive rate, we consider the relationship between the number of active riders and the rate of pay/acceptance rate. As previously noted some riders will naturally leave the service because they make no requests in a month, the likelihood of this is increased the lower the rate of requests for an individual, and the rate of requests of an individual is related to the number of accepted requests of the previous month. Thus this strategy focuses on maximising the rate of requests of users for a period using a low proft/loss pay rate, to keep as many users active as possible, and then switching to a high profit rate. Unfortunately a high rate of requests could take months to build up, and then if the high profit pay rate leads to low accetances, the high request rate will disappear.


## Results:

We can evidently see that the optimal strategy for maximising the profit of this service under these assumptions is to have a fixed rate price in the region of $24 - $26, and further simulations could identify a global maxima to two deicimal places. Even the special cases with more freedom to adapt the rate were both optomised by the same fixed rate across the whole period. There are other more complex adaptations of course, such as a bait and switch rate that changed every month, or an adaptive rate that adapted more intelligently or more actively, ie. focusing on those with high request rates. However, I would theorise that given the evidence we have seen so far, and the relationships present in the data, that these would also be optimised by the same fixed rate.

Once the system is in place and more data has been collected, further analysis could offer improved strategies. For instance the probability of a price point being accepted may vary depending on time of day, weekday vs. weekend effects, holidays, end of month, weather, or person to person. Likewise some of the assumptions of the model, such as the highly varying rate of requests month to month, may prove to be invalid.