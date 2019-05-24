# Python 7zip ReCompress!
Required software
+ [Python 3](https://www.python.org/downloads)
+ [7zip](https://www.7-zip.org/download.html)
## Usage
1. Install required software
	> Ubuntu : `$ sudo apt-get install -y python3 p7zip*`  
	> Windows : download and install [7zip](https://www.7-zip.org/download.html) and [Python](https://www.python.org/downloads)

2. Download [here](https://raw.githubusercontent.com/Wireless4024/Py7zRecompress/master/py7zRecompress.py)  
	##### via command line  
	> Ubuntu : `$ wget https://raw.githubusercontent.com/Wireless4024/Py7zRecompress/master/py7zRecompress.py`  
	> Windows : `> curl -o py7zRecompress.py https://raw.githubusercontent.com/Wireless4024/Py7zRecompress/master/py7zRecompress.py`

3. Run! `$ python py7zRecompress.py <Folder> [Folders...] [-wt work_thread] [-ct compress_thread] [-d deep_count] [-s extension_sensitive] [-dc dictionary_size] [-7z 7zExecutable]`
	> `Folder path ...`          : Folder that contains compress-able files `[7z, xz, zip, jar, rar, gz]`  
	> `-wt int`         : Working thread count (default : `1`)  
	> `-ct int`         : Thread count used by 7zip (default : `3`)  
	> `-d int`          : How deep to re-compress (useful when you have zip inside zip again and again) (default : `2`)  
	> `-s yes|no`       : use compress algorithm same with file extension (default : `no`)  
	> `-dc int`         : size of dictionary in MegaBytes used by `7z` and `xz` (default : `96`)  
	> `-7z path`        : path to 7z executable (default : "`7z.exe`|`7z`")  
	> `-e file_extension;...`   : excluded file extension eg. `-e 7z;rar` will not re-compress `.7z` and `.rar` file  
	> `-i file_extension;...`   : include file extension eg. `-i iso;wim` will re-compress default file extensions and `.iso` and `.wim` file  
	> `-o file_extension;...`   : re-compress only file extension eg. `-o zip` will re-compress only `.zip` file  
	> `-n yes|no`       : do not backup  (default : `no`) 
	> `-t int`          : extract timeout (default : `900` -> 15mins)  
	> `-p string`       : file password (use when archive is locked)  
	> `-ca string`      : additional argument when compress for 7zip  
	> `-ea string`      : additional argument when extract for 7zip  
	> `-skip yes|no`    : skip locked file (default : `yes` if password is empty)  
	
	> `-h` : show all help

	### Example :
	##### you can leave it alone like so
	> `> python py7zRecompress.py "C:\Users\Administrator\Downloads"`  
	> `> python py7zRecompress.py "C:\Users\Administrator\Downloads" "C:\Users\Administrator\Documents"`  
	##### or you can do this
	> `> python py7zRecompress.py "C:\Users\Administrator\Downloads" -wt 2 -ct 8 -d 5 -s no -dc 128`  
	>> `"C:\Users\Administrator\Downloads"` :: scan files inside folder `Downloads`  
	>
	>> `-wt 2` :: let program run 2 instance of 7zip  
	>
	>> `-ct 8` :: let 7z compress file with 8 threads  
	>
	>> `-d 5`  :: let program look up compress-able file inside archive 5 times  
	>
	>> `-s no`  :: re-compress any archive into .7z  
	>
	>> `-dc 128`  :: set dictionary size to 128m  

	### *Note*
	> `Deep` parameter will very very slow if file/folder contains lots of file  

	> _**it will work even it's not efficient**_
