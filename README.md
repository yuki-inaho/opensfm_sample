# Installation
1. Clone this repository
```
git clone https://github.com/yuki-inaho/opensfm_sample.git
```

2. Install python libraries
```
pip3 install -r requirements.txt
```

3. Build OpenSfM

[Read the official document](https://opensfm.readthedocs.io/en/latest/building.html)


4. Convert MP4 file
```
python3 mp4toImages.py -i mp4/movie.mp4
```

5. Generate Dataset
(By running below command, "project" directory will be generate)
```
python3 generate_project_directory.py
```

6. Run below command
```
python3 {OpenSfM Installed directory path}/bin/opensfm_run_all project
```
