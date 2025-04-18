#include <iostream>
#include <fstream>
#include <random>
#include <ctime>
#include <iomanip>
#include <string>
#include <thread>
#include <chrono>
#include <filesystem>

using namespace std;

// 현재 시각 문자열 반환
string getCurrentTime() {
    time_t now = time(0);
    tm t;
    localtime_s(&t, &now);
    char buf[32];
    strftime(buf, sizeof(buf), "%Y-%m-%d %H:%M:%S", &t);
    return string(buf);
}

bool fileExists(const string& name) {
    ifstream f(name.c_str());
    return f.good();
}

// CSV 헤더 존재 여부 확인 후 작성
void writeCsvHeaderIfNeeded(const string& filename) {
    if (!fileExists(filename)) {
        ofstream file(filename);
        file << "timestamp,temperature,gas,power,sound,risk\n";
        file.close();
    }
}

// 센서값 1세트 생성 후 CSV에 추가
void generateAndAppendSensorData(const string& filename) {
    random_device rd;
    mt19937 gen(rd());
    uniform_real_distribution<> temp(30.0, 60.0);
    uniform_real_distribution<> gas(100.0, 250.0);
    uniform_real_distribution<> power(2.0, 6.0);
    uniform_real_distribution<> sound(60.0, 90.0);

    double t = temp(gen);
    double g = gas(gen);
    double p = power(gen);
    double s = sound(gen);
    string timestamp = getCurrentTime();

    string risk = "";
    bool isNormal = true;

    if (t > 50.0) {
        risk += "온도 초과, ";
        isNormal = false;
    }
    if (g > 200.0) {
        risk += "가스 위험, ";
        isNormal = false;
    }
    if (p > 5.0) {
        risk += "전력 과부하, ";
        isNormal = false;
    }
    if (s > 85.0) {
        risk += "소음 위험, ";
        isNormal = false;
    }

    if (isNormal) {
        risk = "정상";
    }
    else {
        risk = risk.substr(0, risk.length() - 2);
    }

    ofstream file(filename, ios::app);
    file << timestamp << "," << fixed << setprecision(2)
        << t << "," << g << "," << p << "," << s << ",\"" << risk << "\"\n";
    file.close();

    cout << "저장됨: " << timestamp << " / 위험: " << risk << endl;
}

int main() {
    string filename = "C:/Users/user/Desktop/산업재해데이터/sensor_result.csv";

    // 헤더 작성 (없을 경우만)
    writeCsvHeaderIfNeeded(filename);

    // 무한 루프 실행 → PyQt에서 종료 버튼으로 제어 가능
    while (true) {
        generateAndAppendSensorData(filename);
        this_thread::sleep_for(chrono::seconds(2));
    }

    return 0;
}
