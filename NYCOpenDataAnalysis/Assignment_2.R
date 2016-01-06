setwd("~/Downloads")

library(ggmap)
library(gridExtra)
library(plyr)

dataset1 <- read.csv("NYPD_Motor_Vehicle_Collisions.csv")

#clean data to remove rows not containing location info
dataset_clean = dataset1[which(regexpr(',',dataset1$LOCATION) !=-1),]

#comm=regexpr(',',dataset_clean$LOCATION)
#parse DATE to get year
dataset_clean$year=substr(dataset_clean$DATE,7,10)

#group by year and count
library(plyr)
dataset_clean$year <- as.numeric(dataset_clean$year)

library(ggplot2)
qplot(year,data=dataset_clean, geom="histogram", binwidth=0.5) + ggtitle("Number of collisions from 2012-2015")
#hist(dataset_clean$year)

#create datasets for each year
d_2012=dataset_clean[which(dataset_clean$year=='2012'),c('LONGITUDE','LATITUDE')]
d_2013=dataset_clean[which(dataset_clean$year=='2013'),c('LONGITUDE','LATITUDE')]
d_2014=dataset_clean[which(dataset_clean$year=='2014'),c('LONGITUDE','LATITUDE')]
d_2015=dataset_clean[which(dataset_clean$year=='2015'),c('LONGITUDE','LATITUDE')]

#use getmap() to get a map of NYC
nyc_plot = ggmap(get_map('NEW YORK, NEW YORK',zoom=12,maptype = "terrain"))

#add 2-simensional density to plot using stat_density2d()
#for all years dataframe
plot2012=nyc_plot+stat_density2d(data = d_2012,aes(x=d_2012$LONGITUDE,y = d_2012$LATITUDE,alpha = .75, fill = ..level..),bins=10,geom='polygon')+
  guides(fill=guide_colorbar(barwidth =1,barheight = 12))+
  scale_alpha(guide=FALSE)+
  xlab('Longitude')+ylab('Latitude')+
  ggtitle('Vehicle Collisions-NYC-2012')

plot2013=nyc_plot+stat_density2d(data = d_2013,aes(x=d_2013$LONGITUDE,y = d_2013$LATITUDE,alpha = .75, fill = ..level..),bins=10,geom='polygon')+
  guides(fill=guide_colorbar(barwidth =1,barheight = 12))+
  scale_alpha(guide=FALSE)+
  xlab('Longitude')+ylab('Latitude')+
  ggtitle('Vehicle Collisions-NYC-2013')

plot2014=nyc_plot+stat_density2d(data = d_2014,aes(x=d_2014$LONGITUDE,y = d_2014$LATITUDE,alpha = .75, fill = ..level..),bins=10,geom='polygon')+
  guides(fill=guide_colorbar(barwidth =1,barheight = 12))+
  scale_alpha(guide=FALSE)+
  xlab('Longitude')+ylab('Latitude')+
  ggtitle('Vehicle Collisions-NYC-2014')

plot2015=nyc_plot+stat_density2d(data = d_2015,aes(x=d_2015$LONGITUDE,y = d_2015$LATITUDE,alpha = .75, fill = ..level..),bins=10,geom='polygon')+
  guides(fill=guide_colorbar(barwidth =1,barheight = 12))+
  scale_alpha(guide=FALSE)+
  xlab('Longitude')+ylab('Latitude')+
  ggtitle('Vehicle Collisions-NYC-2015')

#grid.arrange(plot2012, plot2013, nrow=1,ncol=2)
grid.arrange(plot2012, plot2013,plot2014, plot2015, nrow=2,ncol=2)

#plot 2014 accident densities by borough
#fn boro subsets data by borough and removes all records with missing street name
dataByBorough=function(x){
  boroughSet = dataset_clean[which(dataset_clean$ZIP.CODE != '' & dataset_clean$BOROUGH==x),]
  d_2014_2 = boroughSet[which(boroughSet$year=='2014'),c('LONGITUDE','LATITUDE','ON.STREET.NAME','ZIP.CODE')]
  return(d_2014_2)
}

manhattan = dataByBorough('MANHATTAN')
bronx=dataByBorough('BRONX')
brooklyn=dataByBorough('BROOKLYN')
statIsland =  dataByBorough('STATEN ISLAND')
queens=dataByBorough('QUEENS')

entireSet = rbind(cbind(manhattan,group='MANHATTAN'),
                  cbind(bronx,group='BRONX'),
                  cbind(brooklyn,group='BROOKLYN'),
                  cbind(statIsland,group='STATEN ISLAND'),
                  cbind(queens,group='QUEENS'))
Borough=entireSet$group

col_vals=c('MANHATTAN'='black', 'BRONX'='blue',
           'BROOKLYN'='darkgreen','STATEN ISLAND'='red',
           'QUEENS'='yellow')

#use getmap() to get a map of NYC
nyc_plot = ggmap(get_map('NEW YORK, NEW YORK',zoom=11,maptype = "terrain"))

plot4=nyc_plot+stat_density2d(data=entireSet, geom='polygon',bins = 10, aes(x=entireSet$LONGITUDE,y=entireSet$LATITUDE,fill = Borough, alpha=..level..))+
  scale_fill_manual(values=col_vals)+
  scale_alpha(guide = FALSE)+ 
  xlab('Longitude')+ylab('Latitude')+
  ggtitle('NYC Vehicle Accidents density by Borough, 2014')
plot4


dataByVehicle=function(x){
  vehicleSet = dataset_clean[which(dataset_clean$VEHICLE.TYPE.CODE.1 ==x & dataset_clean$BOROUGH != ''),]
  d_2014_2 = vehicleSet[,c('LONGITUDE','LATITUDE','ON.STREET.NAME','ZIP.CODE','BOROUGH','year')]
  return(d_2014_2)
}

van=dataByVehicle("VAN")
pickup=dataByVehicle("PICK-UP TRUCK")
wagon=dataByVehicle("SPORT UTILITY / STATION WAGON")
passenger=dataByVehicle("PASSENGER VEHICLE")
taxi=dataByVehicle("TAXI")
largeVeh=dataByVehicle("LARGE COM VEH(6 OR MORE TIRES)")
bicycle=dataByVehicle("BICYCLE")
livery=dataByVehicle("LIVERY VEHICLE")
bike=dataByVehicle("MOTORCYCLE")
bus=dataByVehicle("BUS")
#other=dataByVehicle("OTHER")

vehicleEntire = rbind(cbind(van,group="VAN"),
                      cbind(pickup,group="PICK-UP TRUCK"),
                      cbind(largeVeh,group="LARGE COM VEH(6 OR MORE TIRES)"),
                      cbind(wagon,group="SPORT UTILITY / STATION WAGON"),
                      cbind(passenger,group="PASSENGER VEHICLE"),
                      cbind(bicycle,group="BICYCLE"),
                      cbind(livery,group="LIVERY VEHICLE"),
                      cbind(bike,group="MOTORCYCLE"),
                      cbind(bus,group="BUS"),
                      cbind(taxi,group="TAXI"),
                      cbind(other,group="OTHER"))
Vehicle=vehicleEntire$group

colour_vals=c('VAN'='black','PICK-UP TRUCK'='red','BUS'='azure',
              'SPORT UTILITY / STATION WAGON'='orange','PASSENGER VEHICLE'='purple',
              'TAXI'='brown','LARGE COM VEH(6 OR MORE TIRES)'='cyan',
              'BICYCLE'='blue3','LIVERY VEHICLE'='yellow','MOTORCYCLE'='firebrick','OTHER'='azure')

#colour_vals=c('black','red','green','purple','brown','grey','cyan','blue','yellow','gold','orange')

# plot5 = nyc_plot + stat_bin2d(
# aes(x = LONGITUDE, y = LATITUDE, colour = Vehicle, fill = Vehicle),
#   size = .5, bins = 30, alpha = 1/2,
#   data = vehicleEntire
# ) + scale_colour_manual(values = colour_vals)
# plot5

#bubble-chart
plot6 = nyc_plot + geom_point(aes(x = LONGITUDE, y = LATITUDE, colour=Vehicle),
           data = vehicleEntire) + 
          scale_colour_manual(values = colour_vals) +
          scale_alpha(guide = FALSE)+ 
          xlab('Longitude')+
          ylab('Latitude')+
          ggtitle('NYC Vehicle Accidents density by Vehicle Types')
plot6



library(googleVis)
gctx <- gvisGeoChart(zipcode, 
                     locationvar="ON.STREET.NAME", colorvar="V1", 
                     options=list(displayMode="markers", 
                                  region="US-NY", resolution="metros",
                                  height=800,width=600), 
                     chartid="GeoChart_NY")
plot(gctx)

contributingFactor = ddply(dataset_clean, c("CONTRIBUTING.FACTOR.VEHICLE.1"), function(x){count=nrow(x)})
contributingFactor <- contributingFactor[which(contributingFactor$CONTRIBUTING.FACTOR.VEHICLE.1 != ''),]
#pie chart for contributing factors
p <- ggplot(contributingFactor, aes(x=1, y=V1, fill=CONTRIBUTING.FACTOR.VEHICLE.1)) +
  geom_bar(stat="identity") +
  ggtitle("Pie_chart")
p <- p + coord_polar(theta='y')
p <- p +
  # black border around pie slices
  geom_bar(stat="identity", color='black') +
  # remove black diagonal line from legend
  guides(fill=guide_legend(override.aes=list(colour=NA)))
print(p)

# slices <- contributingFactor$V1
# lbls <- contributingFactor$CONTRIBUTING.FACTOR.VEHICLE.1
# pct <- round(slices/sum(slices)*100)
# lbls <- paste(lbls, pct) # add percents to labels 
# lbls <- paste(lbls,"%",sep="") # ad % to labels 
# pie(slices,labels = lbls, col=rainbow(length(lbls)),
#     main="Pie Chart of Countries")

library(colorspace)

#stacked bar according types of collisions
vehicleBar = ddply(vehicleEntire, c("year","group"), function(x){count=nrow(x)})
plot7 <- ggplot(vehicleBar, aes(x=year, y=V1, fill=group)) +
  geom_bar(stat="identity") +
  xlab("Year")+
  scale_fill_hue()+
  ylab("Total Number of Collisions")+
  ggtitle("NYC Types of Vehicle Collisions")
plot7


#zipcode wise heat map in brooklyn
#zipcode = ddply(brooklyn, c("ZIP.CODE","ON.STREET.NAME","LONGITUDE","LATITUDE"), function(x){count=nrow(x)})
zipcode = data.frame(table(brooklyn$ZIP.CODE))
zipmerge=merge(x=brooklyn,y=zipcode,by.x=c('ZIP.CODE'),by.y=c('Var1'))
zipmerge$freqPercentage=round((zipmerge$Freq/length(zipmerge$ZIP.CODE))*1000,digits=0)
zipmerge$freqPercentage=ifelse(zipmerge$freqPercentage==0,1,zipmerge$freqPercentage)
c='red'
palette=colorRampPalette(c('white',c))
colors=palette(max(zipmerge$freqPercentage))

ny_plot = ggmap(get_map('New York,Brooklyn',zoom = 12,maptype = 'toner'))
plot8 = ny_plot + 
  geom_path(data = zipmerge,
            aes(x=zipmerge$LONGITUDE,y=zipmerge$LATITUDE, group=zipmerge$ZIP.CODE), 
            col=colors[zipmerge$freqPercentage])+
  ggtitle('NYC vehicle accidents in Brooklyn by Zipcode') +
  xlab("Longitude") + ylab("Latitude")
plot8

onstreet = brooklyn[which(brooklyn$ZIP.CODE %in% c(11201,11207)),]
tab=data.frame(table(onstreet$ON.STREET.NAME))
onstreetmerge=merge(x=onstreet,y=tab,by.x =c('ON.STREET.NAME'),by.y = c('Var1'))
onstreetmerge$freqPer=round((onstreetmerge$Freq/length(onstreetmerge$ON.STREET.NAME))*1000,digits=0)
onstreetmerge$freqPer=ifelse(onstreetmerge$freqPer==0,1,onstreetmerge$freqPer)
c='red'
pal=colorRampPalette(c('blue',c))
colorStreet=pal(max(onstreetmerge$freqPer))

ny_plot1 = ggmap(get_map('New York,Brooklyn',zoom = 13,maptype = 'toner'))
plot9 = ny_plot1 + 
  geom_path(data = onstreetmerge,
            aes(x=onstreetmerge$LONGITUDE,y=onstreetmerge$LATITUDE, group=onstreetmerge$ON.STREET.NAME), 
            col=colorStreet[onstreetmerge$freqPer])+
  ggtitle('NYC vehicle accidents in Brooklyn Areas 11201 and 11207 by Street Names') +
  xlab("Longitude") + ylab("Latitude")
plot9

#ml
#data(dataset_clean, package = "mlbench")
library(mlbench)
library(e1071)
#split data in train and test
train = dataset_clean[which(dataset_clean$year != '2015' & dataset_clean$BOROUGH != ''),]
test=dataset_clean[which(dataset_clean$year=='2015' & dataset_clean$BOROUGH != ''),]

library("klaR")
library("caret")

# model <- naiveBayes(CONTRIBUTING.FACTOR.VEHICLE.1 ~ ., data = train)
# #model
# #table(predict(model, test, type="raw"))
# #predict(model, test[1:200,], type = "raw")
# (pred <- predict(model, test))
# table(pred, test$BOROUGH)


model <- naiveBayes(VEHICLE.TYPE.CODE.1 ~., data = train)
#model
#table(predict(model, test, type="raw"))
#predict(model, test[1:200,], type = "raw")
#(pred <- predict(model, test))
(pred<- predict(model,test[1,]))
table(pred, test$BOROUGH)


#hypothesis testing


dataset_clean$TIME <- as.character(dataset_clean$TIME)
dataset_clean$TIME <- sapply(strsplit(dataset_clean$TIME,":"),
       function(x) {
         x <- as.numeric(x)
         x[1]+x[2]/60
       }
)
morningData = dataset_clean[which(dataset_clean$TIME < 15.00 & dataset_clean$TIME > 6.00),]
eveningData = dataset_clean[which(dataset_clean$TIME > 15.00 | dataset_clean$TIME < 6.00),]
t.test(morningData$TIME,eveningData$TIME, mu=5.0)


timedata = ddply(dataset_clean, c("TIME"), function(x){count=nrow(x)})
plot10 <- ggplot(timedata, aes(x=TIME, y=V1),col=red) +
  geom_bar(stat="identity") +
  xlab("Time")+
  scale_fill_hue()+
  ylab("Total Number of Collisions")+
  ggtitle("NYC Collision Distribution according to Time")
plot10

library(xlsx)
write.xlsx(timedata, "timedata.xlsx")
