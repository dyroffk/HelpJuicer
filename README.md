# HelpJuicer

HelpJuicer is a tool to dump all the categories, questions, and answers from HelpJuice

https://helpjuice.com/

![juicer](https://media.giphy.com/media/3orifa6xanytJdaaMo/giphy.gif)


## Requirements

  - python3
  - python-requests

## Usage

  - Set necessary environment variables

```
    export HELPJUICE_DOMAIN={companyName}
    export HELPJUICE_API_KEY={apiKey}
```

  - Run juicer

```
    ./juicer.py
```

  - The tool will write the following CSVs to the working directory:

```
    helpjuice_categories.csv  -  A mapping of parent/child category relationships
    helpjuice_questions.csv   -  HelpJuice questions with corresponding answers 
                                 and link to containing categories
```


