import socket
import threading
import time

log_lock = threading.Lock()

upload_semaphore = threading.Semaphore(3)


queue_lock = threading.Lock()
file_condition = threading.Condition(queue_lock)
pending_files_queue = [] # Our shared resource/buffer

def handle_client(client_connection, client_address, client_id):
    print(f"[CLIENT {client_id}] Connected from {client_address}. Waiting for an upload slot...")

    if upload_semaphore._value == 0:
        print(f"❌ [SEMOPHORE BLOCKED] All slots full! Client {client_id} is forced to pause and wait...")
    

    upload_semaphore.acquire()
    print(f"▶️ [SLOT ACQUIRED] Client {client_id} has entered the upload queue.")
    
    try:
        raw_data = client_connection.recv(1024)
        if b"<NAME_END>" in raw_data:
            header, file_bytes = raw_data.split(b"<NAME_END>", 1)
            original_filename = header.decode()
            filename = f"server_received_{original_filename}"
        else:
            filename = f"received_file_{client_id}.dat"
            file_bytes = raw_data

        with open(filename, 'wb') as file:
            file.write(file_bytes) 
            while True:
                data = client_connection.recv(1024)
                if not data:
                    break
                file.write(data)
                import time; time.sleep(1)
                
        print(f"✅ [THREAD {client_id}] Finished downloading {filename}")
        client_connection.close()


        with file_condition:
            pending_files_queue.append(filename)
            print(f"🔔 [BUZZER] Thread {client_id} added {filename} to queue. Buzzing background thread awake!")
            file_condition.notify() 

        with log_lock:
            with open("transfer_log.txt", "a") as log_file:
                log_file.write(f"Client {client_id} successfully sent {filename}.\n")

    finally:
        
        print(f"⚠️ [SLOT RELEASED] Client {client_id} finished. Slot is now free.")
        upload_semaphore.release()
        
def background_processing_buzzer():
    """ This background worker thread takes a nap if there are no files, 
        and gets buzzed awake when a new file lands. """
    print("[BACKGROUND WORKER] Started and running in background...")
    while True:
        with file_condition:
            
            while len(pending_files_queue) == 0:
                print("[BACKGROUND WORKER] No files to process. Taking a nap (sleeping)...😴")
                file_condition.wait() 
            
            
            filename = pending_files_queue.pop(0)
            print(f"[BACKGROUND WORKER] Buzzed awake! ⏰ Processing/Analyzing metadata for: {filename}")
        
        
        time.sleep(2) 


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 5001))
server_socket.listen(5)
print("Server is running on port 5001 with Semaphore and Condition variables active...\n")


bg_thread = threading.Thread(target=background_processing_buzzer, daemon=True)
bg_thread.start()

client_counter = 0
while True:
    client_connection, client_address = server_socket.accept()
    client_counter += 1
    new_thread = threading.Thread(target=handle_client, args=(client_connection, client_address, client_counter))
    new_thread.start()