from map_creator import create_highways_map

def main():
    print("Creating map...")
    m = create_highways_map("above")
    m.save('autostrada_a1_detailed1.html')
    print("Map saved as 'autostrada_a1_detailed1.html'")

if __name__ == "__main__":
    main()
    