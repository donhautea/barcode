import streamlit as st
import pandas as pd
import cv2
from pyzbar.pyzbar import decode
from pydub import AudioSegment
from pydub.playback import play

# Load the dataset
dataset_file = 'inventory_dataset.csv'
try:
    df = pd.read_csv(dataset_file)
except FileNotFoundError:
    df = pd.DataFrame(columns=['Barcode', 'Description', 'Code', 'Purchase Price', 'Selling Price', 'Inventory', 'Remaining Balance', 'Income'])

def scan_barcode():
    # Load beep sound
    song = AudioSegment.from_wav("beep-02.wav")

    # Capture from webcam
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        success, frame = cap.read()
        # Flip the image to make it a mirror image
        frame = cv2.flip(frame, 1)
        # Detect barcodes
        detectedBarcode = decode(frame)

        if not detectedBarcode:
            st.write("No Barcode Detected")
        else:
            # Process detected barcodes
            for barcode in detectedBarcode:
                if barcode.data != "":
                    # Display barcode data on frame
                    cv2.putText(frame, barcode.data.decode('utf-8'), (50, 50), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 255, 255), 2)
                    # Play beep sound
                    play(song)
                    # Save image with detected barcode
                    cv2.imwrite("code.png", frame)
                    # Return the decoded barcode data
                    cap.release()
                    cv2.destroyAllWindows()
                    return barcode.data.decode('utf-8')

        cv2.imshow('Scanner', frame)
        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return None

def check_barcode(barcode):
    return df[df['Barcode'] == barcode]

def add_new_item(barcode):
    st.sidebar.write("Enter item details:")
    description = st.sidebar.text_input("Description")
    code = st.sidebar.text_input("Code")
    purchase_price = st.sidebar.number_input("Purchase Price", min_value=0.0, format="%.2f")
    selling_price = st.sidebar.number_input("Selling Price", min_value=0.0, format="%.2f")
    inventory = st.sidebar.number_input("Inventory", min_value=0, format="%d")
    if st.sidebar.button("Add Item"):
        remaining_balance = inventory
        income = 0

        new_item = pd.DataFrame({
            'Barcode': [barcode],
            'Description': [description],
            'Code': [code],
            'Purchase Price': [purchase_price],
            'Selling Price': [selling_price],
            'Inventory': [inventory],
            'Remaining Balance': [remaining_balance],
            'Income': [income]
        })

        return new_item
    return None

def main():
    st.sidebar.title("Barcode Scanner")
    barcode = st.sidebar.button("Scan Barcode", on_click=scan_barcode)
    
    if barcode:
        result = check_barcode(barcode)

        if not result.empty:
            item = result.iloc[0]
            st.write("\nItem Details:")
            st.write(f"Description: {item['Description']}")
            st.write(f"Code: {item['Code']}")
            st.write(f"Purchase Price: {item['Purchase Price']}")
            st.write(f"Selling Price: {item['Selling Price']}")
            st.write(f"Inventory: {item['Inventory']}")
            st.write(f"Remaining Balance: {item['Remaining Balance']}")
            st.write(f"Income: {item['Income']}\n")
        else:
            st.sidebar.write("Item not found in dataset. Please enter the item details.")
            new_item = add_new_item(barcode)
            if new_item is not None:
                df = pd.concat([df, new_item], ignore_index=True)
                st.sidebar.write("New item added successfully!\n")

                save_changes = st.sidebar.button("Save Changes")
                if save_changes:
                    df.to_csv(dataset_file, index=False)
                    st.sidebar.write("Dataset saved successfully!\n")
    
    st.sidebar.write("Scan another barcode?")

if __name__ == "__main__":
    main()
