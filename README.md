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
	> `Folder` : (`directory`) Folder that contains compress-able files `[7z, xz, zip, jar, rar, gz]`  
	> `-wt work_thread` : (`int`) Working thread count (default : `1`)  
	> `-ct compress_thread` : (`int`) Thread count used by 7zip (default : `3`)  
	> `-d deep_count`   : (`int`) How deep to re-compress (useful when you have zip inside zip again and again) (default : `2`)  
	> `-s extension_sensitive` : (`yes`|`no`) use compress algorithm same with file extension (default : `no`)  
	> `-dc dictionary_size`    : (`int`) size of dictionary in MegaBytes used by `7z` and `xz` (default : `96`)  
	> `-7z 7z_path`     : path to 7z executable (default : "`7z.exe`|`7z`")  
	
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

	> you need to manually delete `old` folder. in case if 7zip crashed or program has accidental terminates your file will be here  

	> please manually extract locked file before it will cause deadlock   
	
	> _**it will work even it's not efficient**_
