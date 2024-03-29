from PyPDF2 import PdfWriter, PdfReader


def split():

    filename = 'test.pdf'
    with open(filename, 'rb') as pdf_file:
        # Create a PDF reader object
        pdf_reader = PdfReader(pdf_file)
    
        # Define the range of pages you want to select (e.g., pages 2 to 4)
        start_page = 3 #แก้เลขตรงนี้
        end_page = 3 #แก้เลขตรงนี้
    
        # Create a new PDF writer object for the selected pages
        pdf_writer = PdfWriter()
    
        for page_num in range(start_page - 1, end_page):
            # Get the current page
            page = pdf_reader.pages[page_num]
    
            # Add the current page to the writer
            pdf_writer.add_page(page)
    
        # Create a new PDF file for the selected pages
        output_filename = 'Split completed'+filename  
        with open(output_filename, 'wb') as output_file:
            # Write the selected pages to the new PDF file
            pdf_writer.write(output_file)
            print('Completed SPLIT process!!')


def rotate():

    filename = 'test.pdf'  #ชื่อไฟล์ที่ต้องการเปลี่ยน เอาไฟล์มาวางที่เดียวกัน
    
    reader = PdfReader(filename)
    writer = PdfWriter()
    
    # Pages to rotate and their corresponding degrees:
    page_numbers = [1]  # Rotate pages 2 and 3
    degre1es = [90]    # Rotate both pages by 90 degrees
    
    # Copy all pages from the original file, rotating specified pages:
    for i in range(len(reader.pages)):
        page = reader.pages[i]
        if i + 1 in page_numbers:
            page.rotate(degre1es[page_numbers.index(i + 1)])
        writer.add_page(page)
    
    # Creat e the output file withrotated pages:
    with open("Rotate completed" + filename, "wb") as fp:
        writer.write(fp)
        print('Completed ROTATE process!!')



while True:
    print("Modify --> Please select an option:")
    print("    1. Split file")
    print("    2. Rotate file")
    print("    3. Exit")
 
    Nofile = input()
 
    if Nofile == '1':
        split()
    elif Nofile == '2':
        rotate()
    elif Nofile == '3':
        print("Exiting the program.")
        break  # Exit the loop if '3' is entered
    else:
        print("Invalid input. Please enter '1', '2', or '3'.")
  

