//#include <iostream>
//#include <fstream>
//#include <cstdlib>
//#include <ctime>
//#include <string>
//#include <sstream>
//#include <iomanip>
//#include <direct.h>   // _mkdir
//#include <io.h>       // _access
//#include <random>     // 정규분포 생성용
//using namespace std;
//
//int main() {
//    // ✅ 난수 생성기 준비
//    random_device rd;
//    mt19937 gen(rd());
//
//    // ✅ 정규분포 설정
//    normal_distribution<float> temp_dist(25.0, 2.0);     // 평균 25도
//    normal_distribution<float> hum_dist(50.0, 8.0);      // 평균 50%
//    normal_distribution<float> co2_dist(600.0, 120.0);   // 평균 600ppm
//    normal_distribution<float> vib_dist(3.0, 1.5);       // 평균 3.0
//    normal_distribution<float> energy_dist(700.0, 150.0);// 평균 700
//
//    // ✅ 저장 경로
//    string folderPath = "../../../../shared/data";
//    string filePath = folderPath + "/sensor_result.csv";
//
//    if (_access(folderPath.c_str(), 0) == -1) {
//        _mkdir(folderPath.c_str());
//    }
//
//    ofstream file(filePath);
//    if (!file.is_open()) {
//        cerr << "sensor_result.csv 파일을 열 수 없습니다." << endl;
//        return 1;
//    }
//
//    file << "timestamp,temperature,humidity,co2,vibration,energy_usage,"
//        << "temp_status,hum_status,co2_status,vib_status,energy_status\n";
//
//    for (int i = 0; i < 50; i++) {
//        time_t now = time(0) + i;
//        struct tm localTime;
//        localtime_s(&localTime, &now);
//
//        stringstream ss;
//        ss << put_time(&localTime, "%Y-%m-%d %H:%M:%S");
//        string timestamp = ss.str();
//
//        // ✅ 정규분포 기반 센서값 생성
//        float temp = temp_dist(gen);
//        float hum = hum_dist(gen);
//        float co2 = co2_dist(gen);
//        float vib = vib_dist(gen);
//        float energy = energy_dist(gen);
//
//        // ✅ 10번째 마다 이상치 삽입
//        if (i % 10 == 0) {
//            int r = rand() % 5;
//            if (r == 0) temp = 33.0;
//            if (r == 1) hum = 25.0;
//            if (r == 2) co2 = 1200.0;
//            if (r == 3) vib = 9.0;
//            if (r == 4) energy = 1200.0;
//        }
//
//        // ✅ 상태 판단
//        string temp_status = (temp > 30) ? "red" : (temp > 27 ? "yellow" : "green");
//        string hum_status = (hum < 35) ? "red" : (hum < 45 ? "yellow" : "green");
//        string co2_status = (co2 > 1000) ? "red" : (co2 > 700 ? "yellow" : "green");
//        string vib_status = (vib > 8.0f) ? "red" : (vib > 5.0f ? "yellow" : "green");
//        string energy_status = (energy > 1000) ? "red" : (energy > 800 ? "yellow" : "green");
//
//        // ✅ CSV 작성
//        file << timestamp << "," << temp << "," << hum << "," << co2 << "," << vib << "," << energy << ","
//            << temp_status << "," << hum_status << "," << co2_status << "," << vib_status << "," << energy_status << "\n";
//    }
//
//    file.close();
//    cout << "sensor_result.csv 생성 완료!" << endl;
//    return 0;
//}

#include <iostream>
#include <fstream>
#include <cstdlib>
#include <ctime>
#include <string>
#include <sstream>
#include <iomanip>
#include <direct.h>   // _mkdir
#include <io.h>       // _access
#include <random>     // 정규분포 생성용
using namespace std;

int main() {
    // ✅ 난수 생성기 준비
    random_device rd;
    mt19937 gen(rd());

    // ✅ 정규분포 설정 (대부분 정상 범위)
    normal_distribution<float> temp_dist(25.0, 2.0);      // 평균 25도, 표준편차 2
    normal_distribution<float> hum_dist(50.0, 8.0);       // 평균 50%, 표준편차 8
    normal_distribution<float> co2_dist(600.0, 120.0);    // 평균 600ppm, 표준편차 120
    normal_distribution<float> vib_dist(3.0, 1.5);        // 평균 3.0, 표준편차 1.5
    normal_distribution<float> energy_dist(700.0, 150.0); // 평균 700, 표준편차 150

    // ✅ 저장 경로
    string folderPath = "../../../../shared/data";
    string filePath = folderPath + "/sensor_result.csv";

    if (_access(folderPath.c_str(), 0) == -1) {
        _mkdir(folderPath.c_str());
    }

    ofstream file(filePath);
    if (!file.is_open()) {
        cerr << "sensor_result.csv 파일을 열 수 없습니다." << endl;
        return 1;
    }

    // ✅ CSV 헤더 작성
    file << "timestamp,temperature,humidity,co2,vibration,energy_usage,";
    file << "temp_status,hum_status,co2_status,vib_status,energy_status\n";

    for (int i = 0; i < 50; i++) {
        time_t now = time(0) + i;
        struct tm localTime;
        localtime_s(&localTime, &now);

        stringstream ss;
        ss << put_time(&localTime, "%Y-%m-%d %H:%M:%S");
        string timestamp = ss.str();

        // ✅ 정규분포 기반 기본값 생성
        float temp = temp_dist(gen);
        float hum = hum_dist(gen);
        float co2 = co2_dist(gen);
        float vib = vib_dist(gen);
        float energy = energy_dist(gen);

        // ✅ 5% 확률로 이상치 삽입
        if (rand() % 100 < 5) {
            int r = rand() % 5;
            if (r == 0) temp = static_cast<float>(rand() % 10 + 40);    // 고온 40~49
            if (r == 1) hum = static_cast<float>(rand() % 15 + 10);     // 건조 10~24
            if (r == 2) co2 = static_cast<float>(rand() % 1000 + 2000); // 과다 CO2 2000~2999
            if (r == 3) vib = static_cast<float>(rand() % 100 + 100) / 10.0f; // 과도 진동 10.0~19.9
            if (r == 4) energy = static_cast<float>(rand() % 500 + 1500);    // 과소비 1500~1999
        }

        // ✅ 상태 판단
        string temp_status = (temp > 30) ? "red" : (temp > 27 ? "yellow" : "green");
        string hum_status = (hum < 35) ? "red" : (hum < 45 ? "yellow" : "green");
        string co2_status = (co2 > 1000) ? "red" : (co2 > 700 ? "yellow" : "green");
        string vib_status = (vib > 8.0f) ? "red" : (vib > 5.0f ? "yellow" : "green");
        string energy_status = (energy > 1000) ? "red" : (energy > 800 ? "yellow" : "green");

        // ✅ CSV 작성
        file << timestamp << "," << temp << "," << hum << "," << co2 << "," << vib << "," << energy << ","
            << temp_status << "," << hum_status << "," << co2_status << "," << vib_status << "," << energy_status << "\n";
    }

    file.close();
    cout << "sensor_result.csv \uc0dd\uc131 \uc644\ub8cc!" << endl;
    return 0;
}
