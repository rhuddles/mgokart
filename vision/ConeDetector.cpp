#include <opencv2/opencv.hpp>
#include <iostream>
#include <array>

using namespace cv;
using namespace std;

class ConeDetector
{
public:
	ConeDetector(array<uint8_t, 6> orangeThresh_) : orangeThresh(orangeThresh_)
	{} 

	vector<KeyPoint> detect(Mat image)
	{
		Mat imageout;
		cvtColor(image, imageout, COLOR_BGR2HSV);

		if(! image.data )
		{
			cout <<  "Could not open or find the image" << std::endl ;
			return {};
		}

		inRange(imageout, Scalar(0, 120, 90), Scalar(200, 225, 255) , imageout);
		//namedWindow( "Color Filter", WINDOW_AUTOSIZE );
		//imshow("Color Filter", imageout);

		GaussianBlur(imageout, imageout, Size(9, 9), 5, 5);
		//namedWindow("Blurred", WINDOW_AUTOSIZE );
		//imshow("Blurred", imageout);

		SimpleBlobDetector::Params params;
		params.filterByInertia = false;
		params.filterByConvexity = false;
		params.filterByCircularity = false;

		params.filterByArea = true;
		params.minArea = 10;
		params.maxArea = 10000000000000;

		params.filterByColor = true;
		params.blobColor = 255;

		SimpleBlobDetector det(params);
		vector<KeyPoint> pts;
		det.detect(imageout, pts);

		return pts;
	}	

private:
	array<uint8_t, 6> orangeThresh;
};
