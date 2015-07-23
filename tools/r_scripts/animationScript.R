# usage: R --vanilla --args <0=obj_1,1=obj_2> <generations> < animationScript.R
# requires a scores-i.rslt file for each generation with each member of the population 
# on a single line in this format:
# <id> <fitness> <obj_1_score> <obj_2_score>

# Since I had 125 generations, you can run the example script with the following command: 

#  $ rm animation.gif; R --vanilla --args 1 < animationScript.R

# or, to plot the other objective:

# $ rm animation.gif; R --vanilla --args 2 < animationScript.R

###################################
library(animation)
args <- commandArgs(trailingOnly = TRUE);


if (args[1]==1){d=2}
if (args[1]==2){d=3}

rangex <- range(0,1) # set rangex to min and max fitness
rangey <- range(0,1) # set rangey to min and max obj score
#Set delay between frames when replaying
ani.options(interval=.15)

filesList <- list.files(path.expand("data/"))
generations <- length(filesList) 

# Begin animation loop
saveGIF({
    layout(matrix(c(1, rep(2, 5)), 6, 1))
   
    par(mar=c(4,4,2,1) + 0.1)
    #for each generation
    for (i in 1:generations) {
        # draw time slider at top of plot
        plot(-5, xlim = c(1,as.numeric(generations)), ylim = c(0, .3), axes = F, xlab = "", ylab = "", main = "Generation")
        abline(v=i, lwd=5, col = rgb(0, 0, 255, 255, maxColorValue=255))
        abline(v=i-1, lwd=5, col = rgb(0, 0, 255, 50, maxColorValue=255))
        abline(v=i-2, lwd=5, col = rgb(0, 0, 255, 25, maxColorValue=255))      
        axis(1)

        #main 2D plot
        #read the scores-i.rslt file for this generation
        tbl <- read.table(paste("data/scores-",i,".rslt",sep=""),colClasses="numeric");
        plot(rangex, rangey, type="n", col="black", ann=FALSE, axes=FALSE, ylim=c(0,1));
        grid(nx=0,ny=NULL,lwd=1, col=1)
        axis(1)
        axis(2)

        for (x in c(1:nrow(tbl))) {
            points(tbl[x,1],tbl[x,d])
        }
        title(ylab="Diversity");
        title(xlab="Fitness");
    }
})

