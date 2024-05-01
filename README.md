# Phishing Detection Toolkit

This toolkit is designed to help users detect phishing attempts by comparing websites against a database of known good domains. It consists of three components:

1. **Terminal-Based Application**: 
    - This application, written in Python, takes two files as input: one containing a list of good domains and another containing a database of random domains. 
    - The application compares the domains in the database with the list of good domains to identify potential phishing attempts.
    - It offers three comparison options:
        - Option 1: Compares URLs and finds similarity using the Levenshtein distance algorithm.
        - Option 2: Takes screenshots of both websites and compares them using a deep learning model (VGG16) to determine similarity.
        - Option 3: Compares the hashes of the favicons of the two websites to identify similarities.
    - This component helps in identifying websites that are attempting to mimic genuine domains.

2. **Server-Side Python Application**:
    - This application contains 28 features extracted from a paper published by the University of California, Irvine, aimed at detecting phishing websites.
    - Various machine learning models are employed to analyze these features.
    - Due to the poor quality of available datasets, a new dataset was manually crafted to ensure accurate results.
    - These features aid in the identification of phishing websites, enhancing overall security.

3. **Firefox Extension**:
    - This extension connects to the server-side Python application.
    - It passively monitors the websites visited by the user and sends this information to the server running the Python application.
    - Based on the analysis results from the server-side application, the extension displays whether a visited website is legitimate or potentially a phishing attempt.

## Built by Team SF90 for Smart India Hackathon 2023

## Installation and Usage

### Terminal-Based Application:
- Clone the repository and navigate to the terminal application directory.
- Run the terminal application with the necessary input files using Python.
- Follow the on-screen instructions to choose the comparison options and analyze the domains.

### Server-Side Python Application:
- Clone the repository and navigate to the server-side application directory.
- Install the required dependencies specified in the `requirements.txt` file using pip.
- Run the Python application, ensuring that the necessary dataset is available for analysis.

### Firefox Extension:
- Install the Firefox extension from the provided `.xpi` file.
- Configure the extension to connect to the server-side Python application.
- Start browsing the web, and the extension will display phishing warnings based on the analysis results.

## Contributing
Contributions to this toolkit are welcome! If you have any ideas for improvements or additional features, please open an issue or submit a pull request.

## Citations
Mohammad,Rami and McCluskey,Lee. (2015). Phishing Websites. UCI Machine Learning Repository. https://doi.org/10.24432/C51W2X.


## Disclaimer
While this toolkit aims to enhance security by detecting phishing attempts, it may not catch all instances of phishing. Users should remain vigilant and exercise caution while browsing the web.

