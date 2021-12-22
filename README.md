# commodities-dashboard
A simply dashboard to view commodities position data based on CFTC reports

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
