class Fat:
    def __init__(self, file):
        self.file = file
        self.file_count = -1

    def print_fs_info(self):
        print(f'Размер сектора составляет {self.get_sec_size()} байт')
        print(f'Размер кластера составляет {self.get_cluster_size()} секторов')
        print(f'Число секторов, занимаемых таблицей FAT равно {self.get_fat_table_sec_count()}')
        print(f'Общее число таблиц FAT равно {self.get_fat_table_count()}')
        print(f'Количество элементов в корневой директории равно {self.get_elements_in_root_directory_count()}')
        print(f'Число зарезервированных секторов равно {self.get_reserved_sec_count()}')
        print(f'Размер директории равен {self.get_dir_size()} секторов')
        print(f'Размер одной записи FAT равен {self.get_one_record_size()} секторов')
        print(f'Смещение корневой директории равно {self.get_dir_offset()} секторов')
        print(f'Тип носителя: {self.get_storage_type()}')
        print(f'Номер активной FAT – {self.get_fat_number()}')
        print(f'Тип файловой системы: {self.get_fs_type()}')

    def print_fs_tree(self):
        root_dir_offset = self.get_dir_offset() * self.get_sec_size()
        print('root')
        self.print_dir(root_dir_offset, '\t')

    def read_file(self, name):
        root_dir_offset = self.get_dir_offset() * self.get_sec_size()
        self.read_file_from_directory(name, root_dir_offset)

    def get_sec_size(self):
        self.file.seek(11)
        return int.from_bytes(self.file.read(2), byteorder='little')

    def get_cluster_size(self):
        self.file.seek(0x0d)
        return int.from_bytes(self.file.read(1), byteorder='little')

    def get_fat_table_sec_count(self):
        self.file.seek(22)
        return int.from_bytes(self.file.read(2), byteorder='little')

    def get_fat_table_count(self):
        self.file.seek(16)
        return int.from_bytes(self.file.read(1), byteorder='little')

    def get_elements_in_root_directory_count(self):
        self.file.seek(17)
        return int.from_bytes(self.file.read(2), byteorder='little')

    def get_reserved_sec_count(self):
        self.file.seek(14)
        return int.from_bytes(self.file.read(1), byteorder='little')

    def get_dir_size(self):
        self.file.seek(0x11)
        record_count = int.from_bytes(self.file.read(2), byteorder='little')
        return int(record_count * 32 / self.get_sec_size())

    def get_one_record_size(self):
        # fat_size
        self.file.seek(0x16)
        return int.from_bytes(self.file.read(2), byteorder='little')

    def get_dir_offset(self):
        return self.get_reserved_sec_count() + self.get_one_record_size() * self.get_fat_table_count()

    def get_storage_type(self):
        self.file.seek(0x15)
        if self.file.read(1) == b'\xf8':
            return 'жесткий диск'
        else:
            return 'гибкий диск'

    def get_fat_number(self):
        self.file.seek(0x28)
        return int.from_bytes(self.file.read(2), byteorder='little')

    def get_fs_type(self):
        self.file.seek(0x36)
        return self.file.read(8).decode()

    def get_name_part(self, cur_pos):
        part = ''
        cur_pos -= 0xb - 1
        self.file.seek(cur_pos)
        try:
            part += self.file.read(10).decode()
        except:
            part += ""

        self.file.seek(cur_pos + 10 + 3)
        try:
            part += self.file.read(12).decode()
        except:
            part += ""

        self.file.seek(cur_pos + 10 + 3 + 12 + 2)
        try:
            part += self.file.read(4).decode()
        except:
            part += ""
        return part

    def print_file_name(self, cur_pos):
        file_name = ''
        self.file.seek(cur_pos)
        cur_attr = int.from_bytes(self.file.read(1), byteorder='little')
        count = 0
        while cur_attr == 0x0f:
            count += 1
            file_name += self.get_name_part(cur_pos)
            cur_pos += 32
            self.file.seek(cur_pos)
            cur_attr = int.from_bytes(self.file.read(1), byteorder='little')
        print(file_name)
        return count * 32

    def get_rec_type(self, cur_pos):
        attr_offset = 8 * 4 + 11
        self.file.seek(cur_pos + attr_offset)
        attr = int.from_bytes(self.file.read(1), byteorder='little')
        if attr == 0x10:
            return 'dir'
        elif attr == 0x20:
            return 'file'

    def print_dir(self, offset, tab):
        file_rec_size = 8 * 2 * 2
        file_attr_offset = 0xb
        cur_pos = offset - file_rec_size
        cur_attr = 0x0f
        while cur_attr == 0x0f:
            cur_pos += self.print_file_name(cur_pos + file_rec_size + file_attr_offset)
            self.file.seek(cur_pos + file_rec_size + file_attr_offset)
            cur_attr = int.from_bytes(self.file.read(1), byteorder='little')

    def get_data_space_offset(self, file_offset):
        # content_offset = 0
        # if file_offset > 0:
        #     self.file.seek(file_offset + 58)
        #     content_offset = int.from_bytes(self.file.read(2), byteorder='little')
        # int(content_offset / self.get_cluster_size())
        return (self.get_dir_size() + self.get_dir_offset() + 1) * self.get_sec_size()

    def print_file_contents(self, offset, size):
        self.file.seek(offset)
        print(self.file.read(size).decode())

    def read_file_from_directory(self, name, offset):
        file_rec_size = 8 * 2 * 4
        cur_pos = offset
        self.file.seek(cur_pos)
        cur_int = int.from_bytes(self.file.read(1), byteorder='little')
        while cur_int == 0x41:
            if self.get_rec_type(cur_pos) == 'file':
                self.file_count += 1
                if self.get_file_name(cur_pos) == name:
                    self.print_file_contents(self.get_data_space_offset(), self.get_file_size(cur_pos))
            elif self.get_rec_type(cur_pos) == 'dir':
                self.file_count += 1
                # FIXME: 16 * 4 ??? (file in dir offset)
                data_offset = self.get_data_space_offset() + 16 * 4
                self.read_file_from_directory(name, data_offset)
            cur_pos += file_rec_size
            self.file.seek(cur_pos)
            cur_int = int.from_bytes(self.file.read(1), byteorder='little')

    def get_file_size(self, offset):
        self.file.seek(offset + 16 * 3 + 12)
        return int.from_bytes(self.file.read(4), byteorder='little')

    # e5 - начало удаленного файла

    # везде идем по атрибутам (то, что 0f)
