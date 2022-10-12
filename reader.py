import struct

#define T_DIR  1   // Directory
#define T_FILE 2   // File
#define T_DEV  3   // Device
FSMAGIC=0x10203040
BSIZE=1024

rawfile = open("fs.img","rb")
rawdata = rawfile.read()
print(len(rawdata))
NDIRECT = 12
dirsiz = 14

def leer(offset, size=None):
    if not size:
        return rawdata[offset:]
    else:
        return rawdata[offset:offset+size]


class SuperBlock(object):
    #  uint magic;        // Must be FSMAGIC
    #  uint size;         // Size of file system image (blocks)
    #  uint nblocks;      // Number of data blocks
    #  uint ninodes;      // Number of inodes.
    #  uint nlog;         // Number of log blocks
    #  uint logstart;     // Block number of first log block
    #  uint inodestart;   // Block number of first inode block
    #  uint bmapstart;    // Block number of first free map block
    def __init__(self, number):
        self.magic, self.size, self.nblocks, self.ninodes, self.nlog, self.logstart, self.inodestart, self.bmapstart = struct.unpack_from('I'*8, leer(BSIZE,4*8))

sblock = SuperBlock(1)#dado por la especificacion del filesystem

class Inode(object):
    #struct dinode {
    #  short type;           // File type
    #  short major;          // Major device number (T_DEV only)
    #  short minor;          // Minor device number (T_DEV only)
    #  short nlink;          // Number of links to inode in file system
    #  uint size;            // Size of file (bytes)
    def __init__(self, number):
        self.number = number
        inodo_size = struct.calcsize("hhhhI"+"I"*(NDIRECT + 1))
        self.tipo, self.major, self.minor, self.nlink, self.size, *self.addrs = struct.unpack_from("hhhhI"+"I"*(NDIRECT + 1), leer(sblock.inodestart*BSIZE+number*inodo_size))
    
    def is_dir(self):
        return self.tipo == 1
    
    def is_file(self):
        return self.tipo == 2
    
    def is_device(self):
        return self.tipo == 3
    
    def get_indirect_addrs(self):
        data = leer(BSIZE*self.addrs[NDIRECT], BSIZE)
        indirect_addrs = [int.from_bytes(data[i:i+4], 'little') 
                          for i in range(0, BSIZE, 4)]
        return indirect_addrs

    def data(self):
        result = b""
        addrs = self.addrs[:NDIRECT] + self.get_indirect_addrs()
        for data_block in addrs:
            if data_block == 0:
                continue
            else:
                result += leer(BSIZE*data_block, BSIZE)
        return result[:self.size]
    def __repr__(self):
        return "Inode(number=%s)" % self.number






i=0
root_inode = Inode(i)
while not root_inode.is_dir():
    i+=1
    root_inode = Inode(i)

print(root_inode)
print(root_inode)

def path_inodo(name, inodo):
    if inodo.is_dir():
        return Directory(name,inodo)
    elif inodo.is_file():
        return File(name, inodo)
    elif inodo.is_device():
        return Device(name, inodo)
    else:
        print(name)
        print(inodo)
        assert False

class Device(object):
    def __init__(self, name, inode):
        assert inode.is_device()
        self.name = name
        self.inode = inode
        self.size = inode.size
    def read(self):
        return self.inode.data()
    def __repr__(self):
        return "Device(\'%s\', %s)" % (self.name, self.inode)

class File(object):
    def __init__(self, name, inode):
        assert inode.is_file()
        self.name = name
        self.inode = inode
        self.size = inode.size
    def read(self):
        return self.inode.data()
    def __repr__(self):
        return "File(\'%s\', %s)" % (self.name, self.inode)

class Directory(object):
    def __init__(self, name, inode):
        assert inode.is_dir()
        self.name = name
        dirents = inode.data()
        archivos = []
        dirents = dirents[16*2:] # tiro . y ..
        while dirents:
            dirent, dirents = dirents[0:16], dirents[16:]
            inum, *namedata = struct.unpack_from("H"+ str(dirsiz) + "c", dirent)
            if inum != 0:
                name = ""
                for c in namedata:
                    if c != b"\x00":
                        name += c.decode("ascii")
                    else:
                        break
                archivos.append(path_inodo(name,Inode(inum)))
        self.archivos = archivos
    def __repr__(self):
        return "Directory(\'%s\', %s)" % (self.name, self.inode)
directorio_raiz = Directory("root",root_inode)


import os

os.mkdir("xv6fs")
path = ["xv6fs"]
def creador(directorio):
    os.mkdir("/".join(path) + "/" + directorio.name)
    path.append(directorio.name)
    for archivo in directorio.archivos:
        if archivo.inode.is_dir():
            creador(archivo)
        elif archivo.inode.is_file():
            f = open("/".join(path) + "/" + archivo.name, "bw")
            f.write(archivo.read())
            f.close()
        else:
            f = open("/".join(path) + "/" + archivo.name, "bw")
            f.write(b"Device file in xv6")
            f.close()

creador(directorio_raiz)


