'''
  1. load the dictionary file into a dictionary
  2. read the file that need to be modified
  3. print the modified file

'''


class UpdateMaster:
    #d = {}

    #  1. load the dictionary file into a dictionary
    @staticmethod
    def load_dictionary(fh, d):
        for l in fh:
            if not l.startswith('#') and l.strip() != '':
                print("**** l:", l)
                k, v = l.split('=')
                d[k.strip()] = v.strip()

    #  2. modify the file
    @staticmethod
    def modify_file(self, fhm):
        for l in fhm:
            k, v = l.split(':')
            self.d[k.strip()] = v.strip()
    @staticmethod
    def modify_master(f, d):
        # Modifiy the file master
        fhm = open(f, 'r+')
        lines = fhm.readlines()
        fhm.close()
        fhm = open(f, 'w+')
        for l in lines:
            print('<---- l:', l)
            #if not l.startswith('#'):
            if "=" in l:
                k, v = l.split('=', 1)
                if k in d.keys():
                   fhm.write('{}={}'.format(k, d[k]))
                   fhm.write('\n')
                else:
                    fhm.write(l)
            else:
                fhm.write(l)
        fhm.close()

