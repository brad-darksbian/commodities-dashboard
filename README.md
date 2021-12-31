# commodities-dashboard
A simple dashboard to view commodities position data based on CFTC reports.

This system is configured to pull one or multiple years of reports from the government website and process them into a consolidated view of several useful chart types.  I regualrly use this for my own analytics work so the repository will update as needs change.  However, I am treating this mostly as a teaching tool, so I will endeavor to keep the code clean and approachable by any skill level.

Within the code, you will find a number of examples of various plotly chart types with ways to lay them out and call them.  Addtionally, there are several examples of Dash configuration such as various call backs and other elements that provide decent examples into the system.  Some of the examples include:

 - Basic construction of a Dash application
 - Bootstrap components
 - Drop Down lists
 - Range Sliders
 - 3D Plots
 - Line and Bar charts
 - Layout configurations
 - Call backs for dynamic updates
 - Modals and associated call backs
 - Data Processing
 - Retreiving online data files
 - Processing files in a dataframe

This is a python project using Dash and plotly to contextualize the content of the DEACOT and Disaggregation reports on futures trading activity provided weekly
by the CFTC.

Details about these reports can be found at:  https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm

To use:

1. Download the files in the repository to a directory.
2. In the support_functions.py file, ensure your paths are correct.

**NOTE** - I developed this on a Mac and run it on a Linux machine.  Files are set to reside in /tmp.  Windows users will need to set an appropriate path.

3. Review the requirements.txt and make sure all libraries are installed.  These are relatively minimal and easily obtained.
4. Run the main.py file using 'python /path/to/directory/main.py'
5. Navigate your browser to the ip address of the machine (perhaps 127.0.0.1 or other if installed remotely) on port 8050.
6. Enjoy!

Use the code how you please.  If you use it as a basis for your own project, be cool and give me a shout out.

Any questions, comments, or concerns - create an issue or just shoot me an email brad@darksbian.com

Brad

**Addendum** - Some users have pointed out to me that when running this code on OSX, you can sometimes get an error like "[SSL: CERTIFICATE_VERIFY_FAILED]".

This is a known issue with python >=3.6 and OSX.  The fix is simple and outlined here:  https://stackoverflow.com/questions/27835619/urllib-and-ssl-certificate-verify-failed-error