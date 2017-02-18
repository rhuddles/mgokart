#ifndef TRAINER_HPP
#define TRAINER_HPP

/**
 * @page trainer RoombeDetector Trainer
 *
 * @tableofcontents
 *
 * @section problems Boundary Problems
 * Its hard to now what color boundaries to use
 *
 * @section process Training Process
 * src/trainer is used to train RoombaDetector. Given an image it will run
 * detection using all different possible color boundaries. Prints all
 * detected roombas in CSV format. The output format is:
 *
 * 1. filename
 * 2. detected x coordinate
 * 3. detected y coordinate
 * 4. black HSV threshold
 * 5. green HSV threshold
 * 6. silver HSV threshold
 *
 * The HSV thresholds are formatted also in CSV as:
 *
 * 1. h lower bound
 * 2. h upper bound
 * 3. s lower bound
 * 4. s upper bound
 * 5. v lower bound
 * 6. v upper bound
 *
 * So, in all, the output CSV file has 3 + (3 * 6) = 21 columns.
 */

#endif /* TRAINER_HPP */
