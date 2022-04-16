library(SimplyAgree)

power_res <- blandPowerCurve(
    samplesizes = seq(10, 10000, 1),
    mu = 0.05, # I don't know what the mean difference between WB and gER is yet, so I said 50 mL
    SD = 0.05, # I don't know what the SD difference between WB and gER is yet
    delta = 0.091, # error expected at a steady-state VO2 (see Robergs, 2010)
    conf.level = .95,
    agree.level = .95
)

head(power_res)

find_n(power_res)
plot(power_res)


