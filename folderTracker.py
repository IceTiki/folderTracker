import os
import os.path
import hashlib
import yaml
import time

def log(*arg):
        for item in arg:
            print(time.strftime("%Y-%m-%d %H:%M:%S|",
                                    time.localtime())+str(item))

class FolderStatus:
    def __init__(self, path='./', yamlPath='.folderStatusHistory.yml'):
        self.path = path
        self.yamlPath = yamlPath
        self.FilePathList()
        self.FileHashList()
        self.FolderStatus()
        self.logHistory()



    def FilePathList(self):
        log(f'遍历检查文件夹({self.path})的状态')
        self.filePath_List = []
        self.folderPath_List = [self.path]
        # 遍历所有文件夹，挑出所有文件。
        # 并挑出所有文件夹，加入到tobeunfold_List中。
        # 备注：for in的机制是遍历tobeunfold_List直到最后一个对象，所以新加入的文件夹也会被遍历到。
        for folder in self.folderPath_List:
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
        log(f'计算文件({self.fileAmount})哈希值')
        for path in self.filePath_List:
            progress += 1
            if progress % 100 == 0:
                log('%d/%d' % (self.fileAmount, progress))
            FileSha256 = self.FileHash(path, 256)
            FileSize = os.path.getsize(path)
            self.amountSize += FileSize
            self.fileHash_List.append('%s|-|%s|-|%d' %
                                      (path, FileSha256, FileSize))
        log('文件哈希计算完毕(大小:%d)(数量:%d)' % (self.amountSize, self.fileAmount))

    def FolderStatus(self):
        log('将数据整理为字典')
        Info = {'Generated_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), 'FolderAmount': len(self.folderPath_List), 'FileAmount': len(
            self.filePath_List), 'AmountSize': self.amountSize, 'RootPath': os.path.abspath(self.path)}
        self.folderData = {'FolderStatus': {'Info': Info, 'FolderList': self.folderPath_List, 'FileHashList': self.fileHash_List}}
        log('数据整理为字典完成')

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

    def logHistory(self):
        if os.path.isfile(self.yamlPath):
            print('查询并生成文件和文件夹的更改')
            old_folderStatus = loadYml(yamlPath)
            foldersAdd = list(set(self.folderData['FolderStatus']['FolderList']).difference(
                set(old_folderStatus['FolderStatus']['FolderList'])))
            foldersDeleted = list(set(old_folderStatus['FolderStatus']['FolderList']).difference(
                set(self.folderData['FolderStatus']['FolderList'])))
            filesAdd = list(set(self.folderData['FolderStatus']['FileHashList']).difference(
                set(old_folderStatus['FolderStatus']['FileHashList'])))
            filesDeleted = list(set(old_folderStatus['FolderStatus']['FileHashList']).difference(
                set(self.folderData['FolderStatus']['FileHashList'])))
            changesInfo = {'Generated_time': time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime()), 'Summary': '%d new files, %d files deleted. %d new folder, %d folder deleted' % (len(filesAdd), len(filesDeleted), len(foldersAdd), len(foldersDeleted))}
            changes = {'FoldersAdd': foldersAdd, 'FoldersDeleted': foldersDeleted,
                    'FilesAdd': filesAdd, 'FilesDeleted': filesDeleted, 'ChangesInfo': changesInfo}

            self.folderData['HistoryChanges'] = old_folderStatus['HistoryChanges']
            self.folderData['HistoryChanges'].append(changes)
        else:
            self.folderData['HistoryChanges']=[{'ChangesInfo': {'Generated_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), 'Summary': "initialize."}}]

    def writeDateIn(self):
        log('开始写入yaml文件')
        file = open(self.yamlPath, 'w', encoding='utf-8')
        yaml.dump(self.folderData, file, allow_unicode=True)
        file.close
        log('写入完毕')
    

    def pathIntercept(self, path: str, level: int):
        new_path=''
        for i in path.split("/")[0:level]:
            new_path+=i+'/'
        return new_path

    def printSet(self, set_:set=set(), head:str=''):
        if set_:
            for i in set_:
                print(head+i)
        else:
            print('',end='')

    def summary(self):
        historyChanges = self.folderData['HistoryChanges']
        if len(historyChanges) < 2:
            print('尚未有记录的变化')
        else:
            # 筛选出内部文件有修改的文件夹
            changes = historyChanges[-1]
            changedFiles = []
            for item in changes['FilesAdd']+changes['FilesDeleted']:
                changedFiles.append(item.split('|-|')[0])
            maxDeep=input('文件夹变动概况(数字:最大展开层数 不输入:默认为3 其他:退出):')
            if maxDeep=='':
                maxDeep = 3
            elif maxDeep.isdigit():
                maxDeep = int(maxDeep)
            else:
                return
            # 逐级展示文件夹变动
            for deep in range(1,maxDeep+1):
                print('==%d级文件夹的变动=='%deep)

                # 新增的文件夹
                set2_=set()
                for item in changes['FoldersAdd']:
                    if item.count('/') == deep:
                        set2_.add(item)
                self.printSet(set2_, '+ ')

                # 删除的文件夹
                set3_=set()
                for item in changes['FoldersDeleted']:
                    if item.count('/') == deep:
                        set3_.add(item)
                self.printSet(set3_, '- ')

                set_=set()
                for item in changedFiles:
                    if item.count('/') >= deep:
                        set_.add(self.pathIntercept(item,deep))
                for item in changes['FoldersAdd']+changes['FoldersDeleted']:
                    if item.count('/') > deep:
                        set_.add(self.pathIntercept(item,deep))
                set_.difference_update(set2_)
                set_.difference_update(set3_)
                self.printSet(set_, '% ')


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
    # 初始化，输入选项
    checkFolderPath = input('请输入需要检查的文件夹(不输入默认为当前目录):\n')
    checkFolderPath = checkFolderPath if checkFolderPath else './'
    yamlPath = input('请输入yaml文件储存地址(不输入默认为当前目录的folderStatusHistory.yml):\n')
    yamlPath = yamlPath if yamlPath else '.folderStatusHistory.yml'

    startTime = time.time()  # 程序开始时间

    # 遍历检查文件夹的状态
    folderData=FolderStatus(path=checkFolderPath, yamlPath=yamlPath)

    # 写入文件
    folderData.writeDateIn()

    endTime = time.time()  # 程序结束时间
    print('\n\n\n\n\n\n\n运行时间%fs\n' % (endTime-startTime))

    print('# 文件夹状态简述')
    folderData.summary()

    input('(按Enter退出)')
