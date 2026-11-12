"""
Скрипт для извлеченияданных из PDF файла
get_pdf_headers - возвращает массив из найденных заголовках в файле
get_pdf_tables - возвращает массив из найденых таблиц(с убранными переносами) - обращение tables[номер таблицы][номер строки][номер данных ячейки]
"""

import re
import pdfplumber
import pymupdf 

def get_learning_form(pdf_path):
    doc = pymupdf.open(pdf_path)
    page = doc.load_page(0)
    text = page.get_text()
    if "Очная, заочная" in text or "очная, заочная" in text:
        return "all"
    else: return "solo"
#возвращает заголовки
def get_pdf_headers(pdf_path):
    #хранит извлеченные заголовки
    extracted_headers = []
    doc = pymupdf.open(pdf_path)
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text()
        
        # Ищем заголовки на странице
        lines = text.split('\n')
        i=0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue


            # Проверяем, начинается ли строка с номера (например "3.1.") для обработки редких случаев ошибки форматирования
            number_match = re.match(r'^(\d+(?:\.\d+)*\.?)\s*$', line)
            
            if number_match:
                #строка только с номером (например "3.1.")
                number = number_match.group(1)
                # Смотрим следующую строку
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line:
                        if next_line.isdigit() or next_line=="\n" or next_line.replace(".","").isdigit():
                            i+=1
                            continue
                        full_header = f"{number} {next_line}"
                        while ".." in full_header:
                            full_header = full_header.replace("..","")
                        extracted_headers.append(full_header)
                        
                        i += 2  # Пропускаем обе строки
                        continue
                i += 1
                continue
            
            # Обычный заголовок в одной строке
            patterns = [
                r'^\d+\.\s+[А-ЯЁа-я]',           # "1. Текст"
                r'^\d+\.\d+\.\s+[А-ЯЁа-я]',      # "1.1. Текст"
                r'^\d+\.\d+\.\d+\.\s+[А-ЯЁа-я]', # "1.1.1. Текст"
                r'^[А-ЯЁ][А-ЯЁ\s\-]+:$',               # "РАЗДЕЛ 1:"
                r'^[А-ЯЁ]{4,}',                        # "ЦЕЛИ И ЗАДАЧИ"
            ]
            
            is_header = False
            for pattern in patterns:
                if re.match(pattern, line):
                    is_header = True
                    break
            
            if is_header:
                extracted_headers.append(line)
            
            i += 1
    
    doc.close()
    return extracted_headers

#возвращает таблицы
def get_pdf_tables(pdf_path,distance_threshold = 90,min_rows = 7):

    #хранит извлеченные таблицы в формате массива, для обращения - [номер таблицы -1][номер строки в таблице -1][номер ячейки -1]
    extracted_tables = []
    previous_table=[]
    with pdfplumber.open(pdf_path) as pdf:
        num = -1
        prev_page=0
        prev_botom_edge=10000
        for page_num, page in enumerate(pdf.pages):
            tables = page.find_tables()
            if tables:
                for table in tables:
                    table_data = table.extract()

                    if not table_data or len(table_data) == 0:
                        continue
                    top_distance = table.bbox[1]
                    #проверяет если таблица сверху страницы, чтобы слить разорванные таблицы
                    if top_distance < distance_threshold:
                        current_rows = len(table_data)

                        # Проверяем предыдущую таблицу, если она или следующая содержит мало строк
                        if previous_table:
                            prev_rows = len(previous_table)


                            # Если хотя бы одна таблица имеет мало строк - объединяем (prev_page - page_num)==-1)
                            if (((current_rows < min_rows or prev_rows < min_rows)  or prev_botom_edge<distance_threshold) and (prev_page - page_num)==-1):

                                #объединение строк с предидущей таблицей
                                for row in table_data:
                                    a = []
                                    for words in row:
                                        if words:
                                            words = words.replace("-\n","")
                                            words = words.replace("\n"," ")
                                            words = words.replace("/ ","/")
                                            a.append(words)
                                        else: a.append(None)
                                    extracted_tables[num].append(a)

                                # Обновляем предыдущую таблицу
                                previous_table = extracted_tables[num]
                                prev_botom_edge = table.bbox[3]
                                # Пропускаем добавление текущей таблицы как отдельной
                                continue

                # Сохраняем текущую таблицу как предыдущую для следующей итерации
                    previous_table =table_data
                    prev_botom_edge = table.bbox[3]
                    prev_page = page_num
                    t = []
                    for row in table_data:
                        a = []
                        for words in row:
                            if words:
                                words = words.replace("-\n","")
                                words = words.replace("\n"," ")
                                words = words.replace("/ ","/")
                                a.append(words)
                            else: a.append(None)
                        t.append(a)
                    extracted_tables.append(t)
                    num+=1
    return extracted_tables

def get_themes(pdf_path, aditional_pages = 5):
    """
    возвращает текст состраниц, где могут быть темы
    """
    doc = pymupdf.open(pdf_path)
    has_req_header = False
    start_page=0
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text()
        
        # Ищем заголовки на странице
        lines = text.split('\n')
        i=0
        while i < len(lines) and not has_req_header:
            line = lines[i].strip()
            if not line:
                i += 1
                continue
            # Проверяем, начинается ли строка с номера (например "3.1.")
            number_match = re.match(r'^(\d+(?:\.\d+)*\.?)\s*$', line)
            
            if number_match:
                # Это строка только с номером (например "3.1.")
                number = number_match.group(1)
                # Смотрим следующую строку - это текст заголовка
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line:
                        if next_line.isdigit() or next_line=="\n" or next_line.replace(".","").isdigit():
                            i+=1
                            continue
                        full_header = f"{number} {next_line}"
                        while ".." in full_header:
                            full_header = full_header.replace("..","")
                        if full_header == "3.3. Содержание дисциплины":
                            has_req_header = True
                            start_page=page_num
                            break
                        i += 2  # Пропускаем обе строки
                        continue
                i += 1
                continue
            
            # Обычный заголовок в одной строке
            patterns = [
                r'^\d+\.\s+[А-ЯЁа-яA-Za-z]',           # "1. Текст"
                r'^\d+\.\d+\.\s+[А-ЯЁа-яA-Za-z]',      # "1.1. Текст"
                r'^\d+\.\d+\.\d+\.\s+[А-ЯЁа-яA-Za-z]', # "1.1.1. Текст"
                r'^[А-ЯЁ][А-ЯЁ\s\-]+:$',               # "РАЗДЕЛ 1:"
                r'^[А-ЯЁ]{4,}',                        # "ЦЕЛИ И ЗАДАЧИ"
            ]
            
            is_header = False
            for pattern in patterns:
                if re.match(pattern, line):
                    is_header = True
                    break
            
            if is_header:
                if line == "3.3. Содержание дисциплины":
                    has_req_header = True
                    start_page=page_num
                    break
        
            
            i += 1
        if has_req_header:
            break
    if has_req_header:
        text = ""
        for page_num in range(start_page,start_page+aditional_pages):
            page = doc.load_page(page_num)
            text += page.get_text().replace("\n","")
            if page_num == start_page:
                text = text[text.find("3.3. Содержание дисциплины"):]


        return (True,text)
    else: return (False,"Отсутствует необходимый раздел")

def get_main_literature(pdf_path, aditional_pages =3):
    """
    возвращает фрагмент текста с основной литературой
    """
    doc = pymupdf.open(pdf_path)
    start_page=0
    text = ""
    temp = []
    result=[]
    for page_num in range(3,len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text(sort=True)
        while "  "in text:
            text = text.replace("  "," ")
        if "Основная литература" in text:
            start_page=page_num
            break
    text = ""
    if start_page!=0:
        for page_num in range(start_page,start_page+aditional_pages):
                page = doc.load_page(page_num)
                text += page.get_text(sort=True)
                while "  "in text:
                    text = text.replace("  "," ")
        text = text[text.find("Основная литература"):]
        text= text[:text.find("4.3")]
        temp = text.split("\n")
        i = 2
        temp_line=""
        for line in temp:
            line = line.strip()
            if line and line !="Основная литература":

                if line[0].isdigit() and int(line[0])==i and line!=',' and line[1]=='.' and temp_line:
                    result.append(temp_line)
                    temp_line=""
                    i+=1
                temp_line+=line.replace("\n", " ")
        result.append(temp_line)

        return result
    else: return
    
    #смотрит на строки, считает порядок литературы, если цифра и совпадает с порядком - новая строка, иначе прибавляем к старой
def get_additional_literature(pdf_path, aditional_pages =3):
    """
    возвращает фрагмент текста с дополнительной литературой
    """
    doc = pymupdf.open(pdf_path)
    start_page=0
    text = ""
    temp = []
    result=[]
    for page_num in range(3,len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text(sort=True)
        while "  "in text:
            text = text.replace("  "," ")
        if "Дополнительная литература" in text:
            start_page=page_num
            break
    text = ""
    if start_page!=0:
        for page_num in range(start_page,start_page+aditional_pages):
                page = doc.load_page(page_num)
                text += page.get_text(sort=True)
                while "  "in text:
                    text = text.replace("  "," ")
        text = text[text.find("Дополнительная литература"):]
        text= text[:text.find("4.4")]
        
        temp = text.split("\n")
        i = 2
        temp_line=""
        for line in temp:
            line = line.strip()
            if line and line !="Дополнительная литература":
                if line[0].isdigit() and int(line[0])==i and line!=',' and line[1]=='.' and temp_line:
                    result.append(temp_line)
                    temp_line=""
                    i+=1
                temp_line+=line.replace("\n", " ")
        result.append(temp_line)
        return result
    else: return
if __name__ == "__main__":
    pdf_file = "RPD_test2.pdf"  
    
    try:
        print(get_additional_literature(pdf_file))
        print(get_main_literature(pdf_file))
    except FileNotFoundError:
        print(f"Ошибка: Файл '{pdf_file}' не найден")
        print("Укажите правильный путь к PDF файлу")
    except Exception as e:
        print(f"Ошибка: {e}")
    