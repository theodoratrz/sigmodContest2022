# SIGMOD 2022 Programming Contest
## Team "BringBackML" - National & Kapodistrian University Of Athens
***
This is our submitted solution for the SIGMOD 2022 [Programming Contest](http://sigmod2022contest.eastus.cloudapp.azure.com/task.shtml).

### Team Members
- [Christos Laspias](https://github.com/ChrisLaspias)
- [Pavlos Spanoudakis](https://github.com/pspanoudakis)
- [Theodora Troizi](https://github.com/theodoratrz)

Advisors:
- Yannis Foufoulas
- Theofilos Mailis

### Task

<div id="task-details-content">
    <p>
        The task is to perform blocking for Entity Resolution, i.e., quickly filter out non-matches 
        (tuple pairs that are unlikely to represent the same real-world entity) in a limited time to 
        generate a small candidate set that contains a limited number of tuple pairs for matching.
    </p>
    <p>
        Participants are asked to solve the task on two product datasets. 
        Each dataset is made of a list of instances (rows) and a list of properties describing them (columns). 
        We will refer to each of these datasets as <b>D<sub>i</sub></b>.
    </p>
    <p>
    For each dataset D<sub>i</sub>, participants are provided with the following resources:
    </p>
    <ul>
        <li><b>X<sub>i</sub></b> : a subset of the instances in D<sub>i</sub></li>
        <li>
            <b>Y<sub>i</sub></b> : matching pairs in X<sub>i</sub> x X<sub>i</sub>. 
            (The pairs not in <b>Y<sub>i</sub></b> are non-matching pairs.)
        </li>
        <li>
            <b>Blocking Requirements</b>: the size of the generated candidate set 
            (i.e., the number of tuple pairs in the candidate set)
        </li>
    </ul>
    <p></p>
    <p>
        Note that matching pairs in <b>Y<sub>i</sub></b> are <b>transitively closed</b> 
        (i.e., if A matches with B and B matches with C, then A matches with C). 
        For a matching pair id<sub>1</sub> and id<sub>2</sub> with id<sub>1</sub> &lt; id<sub>2</sub>, 
        <b>Y<sub>i</sub></b> only includes (id<sub>1</sub>, id<sub>2</sub>) 
        and doesn't include (id<sub>2</sub>, id<sub>1</sub>).
    </p>

<p>
    The goal is to write a program that generates, for each X<sub>i</sub> dataset, 
    a candidate set of tuple pairs for matching X<sub>i</sub> with X<sub>i</sub>. 
    The output must be stored in a CSV file containing the ids of tuple pairs in the candidate set. 
    The CSV file must have two columns: "left;_instance_id" and "right;_instance_id" and the output 
    file <b><u>must be named</u></b> "output.csv;".; The separator must be the comma. 
    Note that <b><u>we do not consider the trivial equi-joins</u></b> 
    (tuple pairs with left_instance_id = right_instance_id) as true matches. 
    For a pair id<sub>1</sub> and id<sub>2</sub> (assume id<sub>1</sub> &lt; id<sub>2</sub>),  
    <b><u>we only include (id<sub>1</sub>, id<sub>2</sub>) 
    and don't include (id<sub>2</sub>, id<sub>1</sub>)</u></b> in "output.csv".
</p>
<p>
    Solutions are evaluated over the complete dataset D<sub>i</sub>. 
    Note that the instances in D<sub>i</sub> (except the sample X<sub>i</sub>) 
    are not provided to the participants. More details are available in the 
    <a href="http://sigmod2022contest.eastus.cloudapp.azure.com/task.shtml?content=evaluation">Evaluation Process</a> section.
</p>
<p>
    Both X<sub>i</sub> and Y<sub>i</sub> are in <b>CSV</b> format.
</p>

<p>
    <u>Example of dataset X<sub>i</sub></u>
    <style>
        table {
        border-collapse:collapse
        }
        td, th {
        border:1px solid #ddd;
        padding:8px;
        }
    </style>
</p>
<table>
    <tbody>
        <tr><th><b>instance_id</b></th><th><b>attr_name_1</b></th><th><b>attr_name_2</b></th><th><b>...</b></th><th><b>attr_name_k</b></th></tr>
        <tr><td>00001</td><td>value_1</td><td>null</td><td>...</td><td>value_k</td></tr>
        <tr><td>00002</td><td>null</td><td>value_2</td><td>...</td><td>value_k</td></tr>
        <tr><td>...</td><td>...</td><td>...</td><td>...</td><td>...</td></tr>
    </tbody>
</table>
<p></p>
    <p>
        <u>Example of dataset Y<sub>i</sub></u>
    </p>
    <table>
        <tbody>
            <tr><th><b>left_instance_id</b></th><th><b>right_instance_id</b></th></tr>
            <tr><td>00001</td><td>00002</td></tr>
            <tr><td>00001</td><td>00003</td></tr>
            <tr><td>...</td><td>...</td></tr>
        </tbody>
    </table>
<p></p>
    <p>
        More details about the datasets can be found in the dedicated 
        <a href="http://sigmod2022contest.eastus.cloudapp.azure.com/task.shtml?content=datasets">Datasets</a> section.
    </p>
    <p>
        <u>Example of output.csv</u>
    </p>
    <table>
        <tbody>
            <tr><th><b>left_instance_id</b></th><th><b>right_instance_id</b></th></tr>
            <tr><td>00001</td><td>00002</td></tr>
            <tr><td>00001</td><td>00004</td></tr>
            <tr><td>...</td><td>...</td></tr>
        </tbody>
    </table>
<p></p>
    <p>
        <b>Output.csv format: </b>The evaluation process expects "output.csv" to have 3000000 tuple pairs. 
        The first 1000000 tuple pairs are for dataset X<sub>1</sub> 
        and the remaining pairs are for datasets X<sub>2</sub>.
        As a result, "output.csv" is formatted accordingly. 
        You can check out the provided <a href="./baseline/blocking.py" download=""><u>baseline solution</u></a> 
        on how to produce a valid "ouput.csv".
    </p>
</div>

### Contest Results
- 11th place out of 55 teams
- Total (average) Recall Score: 46.9% (1st place: 52.9%)
    - 71% on D1 dataset
    - 22.7% on D2 dataset
- < Runtime to be found >

### Requirements
- Python 3.8 or newer
- [`pandas`](https://pypi.org/project/pandas/)
- [`frozendict`](https://pypi.org/project/frozendict/)

### Repository Content
- `baseline` directory:
    - `blocking.py`: The provided baseline solution
- `datasets` directory:
    - `X1.csv` (X1 dataset) & `Y1.csv` (matching pairs for X1)
    - `X2.csv` (X2 dataset) & `Y2.csv` (matching pairs for X2)
- `output_misc` directory: To store secondary `.csv` files, used for analyzing the main `output.csv` file (see below)
- `src` directory:
    - Submitted files:
        - `run.py`: Starting point of the solution
        - `x1_blocking.py`: X1-specific solution logic, definitions & routines
        - `x2_blocking.py`: X2-specific solution logic, definitions & routines
        - `utils.py`: General definitions used by both solutions
    - `output.csv`: **Non-formatted** output for the **given** X1 dataset
    - Scripts for quick usage of ReproZip:
        - `traceAndPack.sh`: Run `run.py` and pack the execution in `submission.rpz`
        - `cleanReprozip.sh`: Clean all files and directories generated by ReproZip (including `submission.rpz`)
    - Scripts for analyzing the solution performance & `output.csv`
        - `compare.py`: Find correct, missed & false positive pairs in `output.csv` and 
        store them (with **titles**) in corresponding `.csv` files, in the `output_misc` directory.
        Also display the number of pairs in each category, as well as the **Recall** score.
        - Bash scripts for separating the `.csv` files generated by `compare.py` by brand, 
        and storing the brand-specific `.csv`'s in `output_misc/false`, `output_misc/missed` and `output_misc/common`.

### Execution
...

### Algorithm Description
...
