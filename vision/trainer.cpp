#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <boost/program_options.hpp>
#include <cmath>
#include <fstream>
#include <mutex>
#include <opencv2/opencv.hpp>
#include <queue>
#include <signal.h>
#include <thread>
#include <utility>
#include <vector>
#include <iostream>

#include "ConeDetector.cpp"

using cv::KeyPoint;
using cv::Mat;
using cv::imread;
using std::array;
using std::cout;
using std::cerr;
using std::endl;
using std::lock_guard;
using std::mutex;
using std::queue;
using std::string;
using std::thread;
using std::vector;

vector<array<uint8_t, 6> > get_oranges();
int parse_options();
void print_cone(const string &fname, const KeyPoint &pt,
		const array<uint8_t, 6> &orange);
void run_on_file(const string &fname);
void print_status(int sig);
void runner();

Mat img;
vector<string> images;
int step_size;
string current_image;
string file;
string path;
int pathStart;
int total_perms;
int cur_perm;
int nthreads;
queue<array<uint8_t, 6>> jobs;
mutex jobs_lock;
mutex out_lock;

array<int, 6> orangeThresh;

/**
 * @brief Load *.json
 */
QJsonObject read_settings(const std::string &filename);

int parse_options(int argc, char **argv)
{
	using boost::program_options::command_line_parser;
	using boost::program_options::notify;
	using boost::program_options::options_description;
	using boost::program_options::positional_options_description;
	using boost::program_options::store;
	using boost::program_options::value;
	using boost::program_options::variables_map;

	QJsonObject settings;

	options_description desc("Allow options");
	desc.add_options()
		("help,h", "produce help message")
		("input-file", value<string>(), "input file")
		("jobs,j", value<int>(), "number of simultaneous jobs")
		;

	positional_options_description pd;
	pd.add("input-file", -1);

	variables_map vm;
	store(command_line_parser(argc, argv).options(desc).positional(pd).run(), vm);
	notify(vm);

	if(vm.count("help"))
	{
		cerr << desc << endl;
		return 1;
	}

	if (vm.count("input-file"))
	{
		file = vm["input-file"].as<string>();
	}
	else
	{
		cerr << "No file(s) given" << endl;
		return 1;
	}

	pathStart = file.find("setting");
	path = file.substr(0, pathStart);

	settings = read_settings(file);

	for (const auto &im : settings["images"].toArray())
	{
		images.push_back(im.toString().toStdString());
	}

	auto tmp = settings["orange_thresh"].toArray();
	for (int i = 0; i < tmp.size(); i++)
	{
		orangeThresh[i] = tmp[i].toInt();
	}

	step_size = settings["step_size"].toInt();

	nthreads = vm.count("jobs") ? vm["jobs"].as<int>() :
					thread::hardware_concurrency();

	// Outputing Settings
	cerr << "Path: " << path << "\n";
	cerr << "Images: ";
	for (size_t i = 0; i < images.size(); i++)
	{
		cerr << images[i] << " ";
	}
	cerr << "\nStepsize: " << step_size << "\nOrange Thresh: [ ";
	for (int i = 0; i < 6; i++)
	{
		cerr << orangeThresh[i] << " ";
	}
	cerr << "]\n";

	return 0;
}

vector<array<uint8_t, 6> > get_oranges()
{
	vector<array<uint8_t, 6> > perms;

	for (int hh = orangeThresh[0] + step_size; hh <= orangeThresh[1];
			hh += step_size)
	{
		for (int hl = orangeThresh[0]; hl < hh; hl += step_size)
		{
			for (int sh = orangeThresh[2] + step_size; sh <= orangeThresh[3];
					sh += step_size)
			{
				for (int sl = orangeThresh[2]; sl < sh; sl += step_size)
				{
					for (int vh = orangeThresh[4] + step_size; vh <= orangeThresh[5];
							vh += step_size)
					{
						for (int vl = orangeThresh[4]; vl < vh; vl += step_size)
						{
							perms.push_back({
									static_cast<uint8_t>(hl),
									static_cast<uint8_t>(hh),
									static_cast<uint8_t>(sl),
									static_cast<uint8_t>(sh),
									static_cast<uint8_t>(vl),
									static_cast<uint8_t>(vh)
									});
						}
					}
				}
			}
		}
	}

	return perms;
}

int main(int argc, char** argv)
{
	if (parse_options(argc, argv) != 0)
	{
		return 1;
	}

	signal(SIGUSR1, print_status);

	for (const auto &fname : images)
	{
		run_on_file(path + fname);
	}

	return 0;
}

void run_on_file(const string &fname)
{
	auto oranges = get_oranges();

	img = imread(fname, CV_LOAD_IMAGE_COLOR);
	current_image = fname;
	total_perms = oranges.size();
	cur_perm = 0;

	cerr << "There are " << total_perms << endl;

	for (const auto &orange : oranges)
	{
		jobs.push(orange);
	}

	thread *runners = new thread[nthreads];
	for (int i = 0; i < nthreads; i++)
	{
		runners[i] = thread(runner);
	}

	for (int i = 0; i < nthreads; i++)
	{
		runners[i].join();
	}

	delete[] runners;
}

void runner()
{
	bool running = true;

	while (running)
	{
		array<uint8_t, 6> orange;

		{
			lock_guard<mutex> g(jobs_lock);

			if (jobs.size() == 0)
			{
				running = false;
				break;
			}
			else
			{
				orange = jobs.front();
				jobs.pop();
			}

			cur_perm++;
		}

		ConeDetector det(orange);

		for (const auto &cone : det.detect(img))
		{
			print_cone(current_image, cone, orange);
		}
	}
}

void print_cone(const string &fname, const KeyPoint &pt,
		const array<uint8_t, 6> &orange)
{
	lock_guard<mutex> g(out_lock);

	cout << fname << "," << pt.pt.x << "," << pt.pt.y;

	for (size_t i = 0; i < orange.size(); i++)
	{
		cout << "," << static_cast<int>(orange[i]);
	}

	cout << endl;
}

void print_status(int sig)
{
	if (sig != SIGUSR1)
	{
		return;
	}

	cerr << current_image << ": ";
	cerr << static_cast<double>(cur_perm) / static_cast<double>(total_perms);
	cerr << endl;
}

QJsonObject read_settings(const std::string &filename)
{
	using std::ifstream;
	using std::string;

	string raw;
	ifstream in(filename);

	while (in.good())
	{
		char buf[2048];
		memset(buf, 0, 2048);
		in.read(buf, 2048);

		raw += string(buf);
	}

	QJsonDocument doc{
		QJsonDocument::fromJson(
				QByteArray{raw.c_str(), static_cast<int>(raw.size())}
				)
	};

	return doc.object();
}
