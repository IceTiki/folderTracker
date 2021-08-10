import os
import os.path
import yaml
import time

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
    yamlfile_Name=input('请输入yaml文件储存地址(不输入默认为当前目录的folderStatusHistory.yml):\n')
    if yamlfile_Name=='':
        yamlfile_Name='folderStatusHistory.yml'
    
    folderStatus=loadYml(yamlfile_Name)['HistoryChanges']
    if len(folderStatus)==0:
        print('尚未有记录的变化')
    else:
        # 筛选出内部文件有修改的文件夹
        changes=folderStatus[-1]
        changesFolders=[]
        for item in changes['FilesAdd']+changes['FilesDeleted']:
            changesFolders.append(item.split('|-|')[0][::-1].split('/',1)[0][::-1])
        changesFolders=set(changesFolders)
        changesFolders.difference_update(set(changes['FoldersAdd']))
        changesFolders.difference_update(set(changes['FoldersDeleted']))

        deep=0
        while 1:
            deep+=1
            empty=1
            try:
                print('有内部文件变化的%d级文件夹'%deep)
                for item in changesFolders:
                    if item.count('/')>=deep:
                        for item_ in item.split('/')[:deep]:
                            print(item_+'/',end='')
                        empty=0
                    print('\n',end='')
            except:
                pass
            try:
                for item in set(changes['FoldersAdd']).intersection_update(set(changes['FoldersDeleted'])):
                    if item.count('/')>=deep+1:
                        for item_ in item.split('/')[:deep]:
                            print(item_+'/',end='')
                        empty=0
                    print('\n',end='')
            except:
                pass
            try:
                print('新增的%d级文件夹'%deep)
                for item in changes['FoldersAdd']:
                    if item.count('/')>=deep:
                        print(item)
                        empty=0
            except:
                pass
            try:
                print('删除的%d级文件夹'%deep)
                for item in changes['FoldersDeleted']:
                    if item.count('/')>=deep:
                        print(item)
                        empty=0
            except:
                pass
            input()
            if empty:
                break
                    
            
            

    input()
