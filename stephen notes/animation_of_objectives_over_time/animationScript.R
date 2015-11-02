# usage: R --vanilla --args <0=obj_1,1=obj_2> <generations> < animationScript.R
# requires a scores-i.rslt file for each generation with each member of the population 
# on a single line in this format:
# <id> <fitness> <obj_1_score> <obj_2_score>

# Since I had 125 generations, you can run the example script with the following command: 

#  $ rm animation.gif; R --vanilla --args 0 125 < animationScript.R

# or, to plot the other objective:

# $ rm animation.gif; R --vanilla --args 1 125 < animationScript.R

# Note that on line 30 of the example script I might have the number of generations hard-coded at 125 when I draw the top slider, so you might want to change that.

###################################
library(animation)
args <- commandArgs(trailingOnly = TRUE);


if (args[1]==0){d=3}
if (args[1]==1){d=4}
#number of generation
t=args[2]

rangex <- range(0,500) # set rangex to min and max fitness
rangey <- range(0,1.2) # set rangey to min and max obj score
#Set delay between frames when replaying
ani.options(interval=.15)

# Begin animation loop
saveGIF({
 
  layout(matrix(c(1, rep(2, 5)), 6, 1))
 
  par(mar=c(4,4,2,1) + 0.1)
    #for each generation
    for (i in 1:t) {
      # draw time slider at top of plot
      plot(-5, xlim = c(1,125), ylim = c(0, .3), axes = F, xlab = "", ylab = "", main = "Generation")
      abline(v=i, lwd=5, col = rgb(0, 0, 255, 255, maxColorValue=255))
      abline(v=i-1, lwd=5, col = rgb(0, 0, 255, 50, maxColorValue=255))
      abline(v=i-2, lwd=5, col = rgb(0, 0, 255, 25, maxColorValue=255))      
      axis(1)

      #main 2D plot
      #read the scores-i.rslt file for this generation
      tbl <- read.table(paste("scores-",i,".rslt",sep=""),colClasses="numeric");
      m=median(tbl[,4])# get median fitness value
      plot(rangex, rangey, type="n", col="black", ann=FALSE, axes=FALSE, ylim=c(0,1.2));
      grid(nx=0,ny=NULL,lwd=1, col=1)
      axis(1)
      axis(2)
      cols<-grey.colors(length(unique(tbl[,4])), start = 0.9, end = 0, gamma = 2.2, alpha = NULL)
 
      for (x in c(1:nrow(tbl))){
      if (tbl[x,4]>m){ p=2 } # above median, draw it as a triangle
      else{ p=3 } # at or below median, draw it as a +
   points(tbl[x,2],tbl[x,d],col=cols[round(tbl[x,5]*length(cols))],lty=2,pch=p)
}
title(ylab="Novelty (mean distance to nearest k=15 hosts in population)");
title(xlab="Fitness (mean reward over 5 or 10 games)");
    }
})

