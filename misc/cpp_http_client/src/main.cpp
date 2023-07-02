#include <iostream>
#include <http_client.h>


using namespace std;


int main(int argc, char **argv) {
    if (argc != 2) {
        cerr << "usage: program url > output_file " << endl;
        return 1;
    }

    string url = argv[1];
    auto response = HttpGet(url);
    if (!response.IsOK()) {
        cerr << "response failed:" << endl;
        cerr << response.Info() << endl;
        return 1;
    }

    cerr << "response OK:" << endl;
    cerr << response.Info() << endl;
    cerr << "=================" << endl;

    cout << response.Content << endl;

    return 0;
}
