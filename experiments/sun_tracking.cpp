//
//  sun_tracking.cpp
//  
//
//  Created by David Abel on 11/3/16.
//
//

#include <stdio.h>
#include <sun_position_algorithms.h>


using namespace std;

// Function declaration (prototype)

int main()
{
    int number=0, result;
    
    // User input must be an integer number between 1 and 10
    while(number<1 || number>10)
    {
        cout << "Integer number = ";
        cin >> number;
    }
    
    // Function call and assignment of return value to result
    result = Factorial(number);
    
    //Output result
    cout << "Factorial = " << result << endl;
    return 0;
}
