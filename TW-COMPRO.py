import struct
import os

# เปลี่ยน record_format เพื่อให้ stock เป็นจำนวนเต็ม
record_format = 'i 20s 20s i 30s'  # record_id, name, description, stock (int), supplier
record_size = struct.calcsize(record_format)

def add_record(file, record_id, name, description, stock, supplier):
    with open(file, 'ab') as f:
        name_bytes = name.encode('utf-8').ljust(20, b'\x00')[:20]
        description_bytes = description.encode('utf-8').ljust(20, b'\x00')[:20]
        supplier_bytes = supplier.encode('utf-8').ljust(30, b'\x00')[:30]
        packed_data = struct.pack(record_format, record_id, name_bytes, description_bytes, stock, supplier_bytes)
        f.write(packed_data)

def display_all_records(file):
    print(f"{'ID':<8} {'Name':<20} {'Description':<20} {'Stock':<10} {'Supplier':<30}")
    print("-" * 80)
    with open(file, 'rb') as f:
        while record := f.read(record_size):
            if len(record) < record_size:
                print("Record size mismatch. Skipping record.")
                continue

            try:
                record_id, name_bytes, description_bytes, stock, supplier_bytes = struct.unpack(record_format, record)
                name = name_bytes.decode('utf-8').strip('\x00')
                description = description_bytes.decode('utf-8').strip('\x00')
                supplier = supplier_bytes.decode('utf-8').strip('\x00')
                print(f"{record_id:<8} {name:<20} {description:<20} {stock:<10} {supplier:<30}")
            except UnicodeDecodeError as e:
                print(f"Error decoding record: {e}. Skipping record.")
            except struct.error as e:
                print(f"Error unpacking record: {e}. Skipping record.")

def search_record(file, key):
    with open(file, 'rb') as f:
        while record := f.read(record_size):
            if len(record) < record_size:
                print("Record size mismatch. Skipping record.")
                continue

            try:
                record_id, name_bytes, description_bytes, stock, supplier_bytes = struct.unpack(record_format, record)
                name = name_bytes.decode('utf-8').strip('\x00')

                # ตรวจสอบการพิมพ์เพื่อช่วยในการดีบัก
                print(f"Comparing with ID: {record_id}, Name: {name}")

                if isinstance(key, int):  # ค้นหาด้วย record_id
                    if key == record_id:
                        return record_id, name, description_bytes.decode('utf-8').strip('\x00'), stock, supplier_bytes.decode('utf-8').strip('\x00')
                elif isinstance(key, str):  # ค้นหาด้วย name
                    if key.lower() == name.lower():  # เปรียบเทียบแบบไม่สนใจตัวพิมพ์ใหญ่/เล็ก
                        return record_id, name, description_bytes.decode('utf-8').strip('\x00'), stock, supplier_bytes.decode('utf-8').strip('\x00')
            except struct.error as e:
                print(f"Error unpacking record: {e}. Skipping record.")
            except UnicodeDecodeError as e:
                print(f"Error decoding record: {e}. Skipping record.")


    return None  # หากไม่พบข้อมูล

def update_record(file, key, new_description=None, new_stock=None, new_supplier=None):
    records = []
    with open(file, 'rb') as f:
        while record := f.read(record_size):
            if len(record) < record_size:
                print("Record size mismatch. Skipping record.")
                continue

            try:
                record_id, name_bytes, description_bytes, stock, supplier_bytes = struct.unpack(record_format, record)
                records.append((record_id, name_bytes, description_bytes, stock, supplier_bytes))
            except struct.error as e:
                print(f"Error unpacking record: {e}. Skipping record.")
                continue

    with open(file, 'wb') as f:
        for record in records:
            if record[0] == key:
                # อัปเดตข้อมูลที่ต้องการ
                if new_description is not None:
                    description_bytes = new_description.encode('utf-8')[:50].ljust(50, b'\x00')  # ขนาด 50 ไบต์
                else:
                    description_bytes = record[2]
                
                if new_stock is not None:
                    stock = new_stock
                else:
                    stock = record[3]

                if new_supplier is not None:
                    supplier_bytes = new_supplier.encode('utf-8')[:50].ljust(50, b'\x00')  # ขนาด 50 ไบต์
                else:
                    supplier_bytes = record[4]

                record = (record[0], record[1], description_bytes, stock, supplier_bytes)
            f.write(struct.pack(record_format, *record))

def delete_record(file, key):
    records = []
    with open(file, 'rb') as f:
        while record := f.read(record_size):
            records.append(struct.unpack(record_format, record))
    
    with open(file, 'wb') as f:
        for record in records:
            if record[0] != key:
                f.write(struct.pack(record_format, *record))

def generate_report(file):
    print("Generating report...")
    display_all_records(file)

# Main loop
def main():
    file = 'data.bin'
    while True:
        print("""
        1. Add new record
        2. Display all records
        3. Search record by ID or Name
        4. Update record
        5. Delete record
        6. Generate report
        7. Exit
        """)
        choice = input("Select an option: ")

        if choice == '1':
            record_id = int(input("Enter Record ID: "))
            name = input("Enter Name: ")
            description = input("Enter Description: ")
            stock = int(input("Enter Stock: "))
            supplier = input("Enter Supplier: ")
            add_record(file, record_id, name, description, stock, supplier)
        elif choice == '2':
            display_all_records(file)
        elif choice == '3':
            key = input("Enter Record ID or Name: ")
            if key.isdigit():
                key = int(key)
            result = search_record(file, key)
            if result:
                print(f"Record found: {result}")
            else:
                print("Record not found.")
        elif choice == '4':
            key = int(input("Enter Record ID to update: "))
            new_description = input("Enter new description (or leave blank to keep unchanged): ")
            new_stock = input("Enter new stock (or leave blank to keep unchanged): ")
            new_supplier = input("Enter new supplier (or leave blank to keep unchanged): ")

            new_stock = int(new_stock) if new_stock else None
            
            update_record(file, key, new_description if new_description else None,
                          new_stock,
                          new_supplier if new_supplier else None)
        elif choice == '5':
            key = int(input("Enter Record ID to delete: "))
            delete_record(file, key)
        elif choice == '6':
            generate_report(file)
        elif choice == '7':
            print("Exiting...")
            break
        else:
            print("Invalid choice!")

if __name__ == '__main__':
    main()
