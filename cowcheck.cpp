#include<iostream>
#include<fstream>
#include<cmath>
#include<set>
using namespace std;
const double phi = (1 + sqrt(5))/2;
int M, N, T, X, Y;
set<pair<int, int> > cold;
main()
{
    freopen("cowcheck.in", "r", stdin);
    freopen("cowcheck.out", "w", stdout);
    cin >> M >> N >> T;
    for (int n = 0;; n++)
    {
        int x_n = floor(n*phi), y_n = floor(n*phi*phi);
        if (x_n>=M||y_n>=N) break;
        cold.insert(make_pair(x_n, y_n));
    }
    for (int i = 0; i < T; i++)
    {
        cin >> X >> Y;
        if (cold.find(make_pair(min(X, Y), max(X, Y)))==cold.end()) 
            cout << "Bessie" << endl;
        else cout << "Farmer John" << endl;
    }
}
