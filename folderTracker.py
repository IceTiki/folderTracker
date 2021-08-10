import os
import os.path
import hashlib
import yaml
import time


class FolderFilesHashList:
    def __init__(self, path='./', isLog=1):
        self.path = path
        self.isLog = isLog
        self.FilePathList()
        self.FileHashList()
        self.FolderStatus()

    def log(self, *arg):
        if self.isLog == 1:
            for item in arg:
                print(time.strftime("%Y-%m-%d %H:%M:%S|",
                                    time.localtime())+str(item))
        else:
            pass

    def FilePathList(self):
        self.filePath_List = []
        self.folderPath_List = [self.path]
        # 遍历所有文件夹，挑出所有文件。
        # 并挑出所有文件夹，加入到tobeunfold_List中。
        # 备注：for in的机制是遍历tobeunfold_List直到最后一个对象，所以新加入的文件夹也会被遍历到。
        for folder in self.folderPath_List:
            self.log('正在获取文件夹\"%s\"的文件列表' % folder)
            for item in os.listdir(folder):
                itempath = folder+item
                if os.path.isfile(itempath):
                    self.filePath_List.append(itempath)
                elif os.path.isdir(itempath):
                    self.folderPath_List.append(itempath+'/')

    def FileHashList(self):
        self.fileHash_List = []
        self.amountSize = 0
        self.fileAmount = len(self.filePath_List)
        progress = 0
        self.log('开始计算文件(%d)哈希值' % self.fileAmount)
        for path in self.filePath_List:
            progress += 1
            if progress % 100 == 0:
                self.log('%d/%d' % (self.fileAmount, progress))
            FileSha256 = self.FileHash(path, 256)
            FileSize = os.path.getsize(path)
            self.amountSize += FileSize
            self.fileHash_List.append('%s|-|%s|-|%d' %
                                      (path, FileSha256, FileSize))
        self.log('文件哈希计算完毕(大小:%d)(数量:%d)' % (self.amountSize, self.fileAmount))

    def FolderStatus(self):
        self.log('开始将数据整理为字典')
        Info = {'Generated_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), 'FolderAmount': len(self.folderPath_List), 'FileAmount': len(
            self.filePath_List), 'AmountSize': self.amountSize, 'RootPath': os.path.abspath(self.path)}
        self.folderStatus = {'FolderStatus': {
            'Info': Info, 'FolderList': self.folderPath_List, 'FileHashList': self.fileHash_List}, 'HistoryChanges': []}
        self.log('数据整理为字典完成')

    def FileHash(self, filepath, HashType):
        if os.path.isfile(filepath):
            try:
                with open(filepath, "rb") as f:
                    if HashType == 1:
                        hashObj = hashlib.sha1()
                    if HashType == 224:
                        hashObj = hashlib.sha224()
                    if HashType == 256:
                        hashObj = hashlib.sha256()
                    if HashType == 384:
                        hashObj = hashlib.sha384()
                    if HashType == 512:
                        hashObj = hashlib.sha512()
                    if HashType == 5:
                        hashObj = hashlib.md5()

                    for byte_block in iter(lambda: f.read(1048576), b""):
                        hashObj.update(byte_block)
                    return hashObj.hexdigest()
            except Exception as e:
                return 'Error!'
        else:
            return 'Error!I\'m a folder!'


def loadYml(ymlFileName='dict.yml'):
    file = open(ymlFileName, 'r', encoding="utf-8")
    dict_ = yaml.load(file, Loader=yaml.FullLoader)
    file.close()
    return dict_


def writeYml(dict_: dict, ymlFileName='dict.yml'):
    file = open(ymlFileName, 'w', encoding='utf-8')
    yaml.dump(dict_, file, allow_unicode=True)
    file.close


if __name__ == '__main__':
    checkFolderPath=input('请输入需要检查的文件夹(不输入默认为当前目录):\n')
    if checkFolderPath=='':
        checkFolderPath='./'
    yamlfile_Name=input('请输入yaml文件储存地址(不输入默认为当前目录的folderStatusHistory.yml):\n')
    if yamlfile_Name=='':
        yamlfile_Name='folderStatusHistory.yml'
    isLog=input('是否需要详细日志输出?(是:1 否:任意输入):\n')
    if isLog=='1':
        isLog=1
    else:
        isLog=0

    startTime = time.time()  # 程序开始时间

    print('开始生成%s的状态'%checkFolderPath)
    now_folderStatus = FolderFilesHashList(path=checkFolderPath,isLog=isLog).folderStatus

    if os.path.isfile(yamlfile_Name):
        print('查询并生成 文件和文件夹的更改')
        old_folderStatus = loadYml(yamlfile_Name)
        foldersAdd = list(set(now_folderStatus['FolderStatus']['FolderList']).difference(
            set(old_folderStatus['FolderStatus']['FolderList'])))
        foldersDeleted = list(set(old_folderStatus['FolderStatus']['FolderList']).difference(
            set(now_folderStatus['FolderStatus']['FolderList'])))
        filesAdd = list(set(now_folderStatus['FolderStatus']['FileHashList']).difference(
            set(old_folderStatus['FolderStatus']['FileHashList'])))
        filesDeleted = list(set(old_folderStatus['FolderStatus']['FileHashList']).difference(
            set(now_folderStatus['FolderStatus']['FileHashList'])))
        changesInfo = {'Generated_time': time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime()), 'Summary': '%d new files, %d files deleted. %d new folder, %d folder deleted' % (len(filesAdd), len(filesDeleted), len(foldersAdd), len(foldersDeleted))}
        changes = {'FoldersAdd': foldersAdd, 'FoldersDeleted': foldersDeleted,
                   'FilesAdd': filesAdd, 'FilesDeleted': filesDeleted, 'ChangesInfo': changesInfo}
        
        now_folderStatus['HistoryChanges'] = old_folderStatus['HistoryChanges']
        now_folderStatus['HistoryChanges'].append(changes)
    else:
        pass

    print('开始写入文件(%s)'%yamlfile_Name)
    writeYml(now_folderStatus, yamlfile_Name)    
    
    endTime = time.time()  # 程序结束时间
    print('运行时间%fs\n按Enter退出' % (endTime-startTime))
    input()
