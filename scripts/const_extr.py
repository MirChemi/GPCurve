import pdfplumber


def extract_const(file_or_folder, data_filename=''):
    if '.pdf' not in file_or_folder:
        data_filename_pdf = data_filename.replace('.txt', '.pdf')
        with pdfplumber.open(data_filename_pdf) as pdf:
            seq_tbl = pdf.pages[0].extract_tables(table_settings={})[0]
        for i in range(len(seq_tbl)):
            for j in range(len(seq_tbl[i])):
                if 'Sequence' in str(seq_tbl[i][j]):
                    seq_list1 = str(seq_tbl[i][j]).split('\n')
                    break
        for i in range(len(seq_list1)):
            if 'Sequence' in str(seq_list1[i]):
                seq_list2 = str(seq_list1[i]).split(': ')
                break
        for i in range(len(seq_list2)):
            if '(' in str(seq_list2[i]):
                s = seq_list2[i]
                if "RI" in s:
                    gpc_type = "RI"
                else:
                    gpc_type = "UV"
                break
        const_filename = f'{file_or_folder}/{s[6]}{s[7]}{s[8]}{s[9]}{s[3]}{s[4]}{s[0]}{s[1]}{gpc_type}.pdf'
    else:
        const_filename = file_or_folder
    print(f'extracting constants from {const_filename}')

    with pdfplumber.open(const_filename) as pdf:
        const_tbl = pdf.pages[0].extract_tables(table_settings={})


    for i in range(len(const_tbl)):
        for j in range(len(const_tbl[i])):
            if const_tbl[i][j] == ['C0', 'C1', 'C2', 'C3']:
                const_list = const_tbl[i][j + 1]

    const = []
    for i in range(len(const_list)):
        const.append(float(const_list[i].replace(' ', '').replace(',', '.')))

    return const
