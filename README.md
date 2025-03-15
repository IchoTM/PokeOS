# PokédexOS

A Linux-based operating system that transforms your computer into a fully functional Pokédex from the Pokémon series. This custom OS provides an authentic Pokédex experience with a modern twist.

## Features

- 🖥️ Custom Linux-based operating system
- 📱 Authentic Pokédex interface
- 🔍 Real-time Pokémon information lookup
- 🎮 D-pad navigation system
- 💡 Status LED indicators
- 🔊 Classic Pokédex sound effects
- 🌐 Integration with PokéAPI for accurate data
- 🎨 Retro-modern design

## System Requirements

- x86_64 compatible computer
- 2GB RAM minimum
- 8GB storage space
- Internet connection for Pokémon data retrieval

## Installation

1. Clone the repository:
```bash
git clone https://github.com/IchoTM/PokeOS
cd pokedexos
```

2. Run the setup script:
```bash
chmod +x setup.sh
sudo ./setup.sh
```

3. Generate the boot sound:
```bash
sudo python3 create_boot_sound.py
```

4. Reboot your system:
```bash
sudo reboot
```

## Usage

1. Power on the system using the power button (⏻)
2. Wait for the boot sequence to complete
3. Use the search bar to look up Pokémon
4. Navigate through the interface using the D-pad:
   - ↑: Previous Pokémon
   - ↓: Next Pokémon
   - ←/→: Navigate through information pages
   - ●: Select/Confirm

## Customization

The system can be customized by modifying the following files:
- `/etc/pokedexos/themes/` - Visual themes
- `/etc/pokedexos/sounds/` - System sounds
- `/etc/pokedexos/database/` - Local Pokémon database

## Troubleshooting

### Common Issues

1. **Screen not displaying**
   - Check X server configuration
   - Verify display permissions

2. **No sound**
   - Check ALSA/PulseAudio configuration
   - Verify sound file permissions

3. **Network connectivity**
   - Check network-manager service status
   - Verify internet connection

### Debug Mode

To start the system in debug mode:
```bash
DEBUG=1 python3 /opt/pokedexos/main.py
```

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) before submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- The Pokémon Company for inspiration
- PokéAPI for Pokémon data
- The Linux community
- All contributors and testers

## Contact

For support or queries, please open an issue on GitHub or contact the maintainers. 