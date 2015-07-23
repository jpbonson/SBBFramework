# requires a i.gen file for each generation with each member of the population 
# on a single line in this format:
# <fitness> <test_score> <obj_1_score> <obj_2_score>
#
# Usage:
# rm *.gif; R --vanilla < animationScript.R

###################################
library(animation)

create_chart <- function(chart_name, score_name, score_index, diversity_name, diversity_index, print_at_each_generation) {
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
            if(i == 1 || i %% print_at_each_generation == 0) {
                # draw time slider at top of plot
                plot(-5, xlim = c(1,as.numeric(generations)), ylim = c(0, .3), axes = F, xlab = "", ylab = "", main = "Generation")
                abline(v=i, lwd=5, col = rgb(0, 0, 255, 255, maxColorValue=255))
                abline(v=i-1, lwd=5, col = rgb(0, 0, 255, 50, maxColorValue=255))
                abline(v=i-2, lwd=5, col = rgb(0, 0, 255, 25, maxColorValue=255))      
                axis(1)

                #main 2D plot
                #read the scores-i.gen file for this generation
                tbl <- read.table(paste("data/",i,".gen",sep=""),colClasses="numeric");
                plot(rangex, rangey, type="n", col="black", ann=FALSE, axes=FALSE, ylim=c(0,1));
                grid(nx=0,ny=NULL,lwd=1, col=1)
                axis(1)
                axis(2)

                for (x in c(1:nrow(tbl))) {
                    points(tbl[x,score_index],tbl[x,diversity_index], col=rgb(0, 0, 0, 0.5))
                }
                title(ylab=diversity_name);
                title(xlab=score_name);
            }
        }
    }, movie.name = chart_name)
}


create_chart("training_vs_diversity1.gif", "Training Score", 1, "Diversity 1", 3, 1);
create_chart("training_vs_diversity2.gif", "Training Score", 1, "Diversity 2", 4, 1);
create_chart("diversity1_vs_diversity2.gif", "Diversity 1", 3, "Diversity 2", 4, 1);
validate_after_each_generation = 25
create_chart("test_vs_diversity1.gif", "Test Score", 2, "Diversity 1", 3, validate_after_each_generation);
create_chart("test_vs_diversity2.gif", "Test Score", 2, "Diversity 2", 4, validate_after_each_generation);
create_chart("train_vs_test.gif", "Training Score", 1, "Test Score", 2, validate_after_each_generation);