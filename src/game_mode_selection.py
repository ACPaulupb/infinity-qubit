#!/usr/bin/env python3
"""
Game Mode Selection Window for Infinity Qubit
Allows users to choose between different game modes with video background.
"""

import sys
import tkinter as tk
import tkinter.messagebox as messagebox
import cv2
from PIL import Image, ImageTk
import threading
import time

from q_utils import get_colors_from_file, extract_color_palette

sys.path.append('..')
from run import PROJECT_ROOT, get_resource_path

# Get color palette
color_file_path = get_resource_path('config/color_palette.json')
palette = extract_color_palette(get_colors_from_file(color_file_path), 'game_mode_selection')

class GameModeSelection:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Infinity Qubit - Game Mode Selection")

        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Window dimensions (slightly larger for better video display)
        window_width = 1000
        window_height = 750

        # Center the window
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.configure(bg=palette['black'])
        self.root.resizable(False, False)

        # Store dimensions
        self.window_width = window_width
        self.window_height = window_height

        # Video background variables
        self.video_cap = None
        self.video_label = None
        self.video_running = False
        self.video_thread = None

        # Initialize sound system
        try:
            import pygame
            pygame.mixer.init()
            self.sound_enabled = True
        except:
            self.sound_enabled = False

        self.setup_video_background()
        self.create_selection_ui()

        # Make sure window is focused and on top
        self.root.lift()
        self.root.focus_force()

        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_video_background(self):
        """Setup video background"""
        try:
            # Loading video file
            video_path = get_resource_path('resources/images/quantum_background.mp4')
            self.video_cap = cv2.VideoCapture(video_path)

            if not self.video_cap.isOpened():
                print("Warning: Could not open video file. Using fallback background.")
                self.video_cap = None
                self.create_fallback_background()
                return

            # Create video label
            self.video_label = tk.Label(self.root, bg=palette['black'])
            self.video_label.place(x=0, y=0, relwidth=1, relheight=1)

            # Start video playbook
            self.video_running = True
            self.video_thread = threading.Thread(target=self.play_video, daemon=True)
            self.video_thread.start()

        except Exception as e:
            print(f"Error setting up video background: {e}")
            self.video_cap = None
            self.create_fallback_background()

    def play_video(self):
        """Play video in background thread"""
        if not self.video_cap:
            return

        fps = self.video_cap.get(cv2.CAP_PROP_FPS)
        frame_delay = 1.0 / fps if fps > 0 else 1.0 / 30  # Default to 30fps

        while self.video_running:
            try:
                ret, frame = self.video_cap.read()

                if not ret:
                    # Loop video
                    self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue

                # Resize frame to window size
                frame = cv2.resize(frame, (self.window_width, self.window_height))

                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Convert to PIL Image
                pil_image = Image.fromarray(frame_rgb)

                # Apply dark overlay for better text readability
                overlay = Image.new('RGBA', pil_image.size, (0, 0, 0, 100))
                pil_image = pil_image.convert('RGBA')
                pil_image = Image.alpha_composite(pil_image, overlay)
                pil_image = pil_image.convert('RGB')

                # Convert to PhotoImage
                photo = ImageTk.PhotoImage(pil_image)

                # Update video label
                if self.video_label and self.video_running:
                    self.video_label.configure(image=photo)
                    self.video_label.image = photo  # Keep a reference

                time.sleep(frame_delay)

            except Exception as e:
                print(f"Error in video playback: {e}")
                break

    def create_fallback_background(self):
        """Create animated fallback background if video fails"""
        # Create animated quantum-themed background
        canvas = tk.Canvas(self.root, width=self.window_width, height=self.window_height,
                          bg=palette['background'], highlightthickness=0)
        canvas.place(x=0, y=0)

        # Draw animated particles/quantum effects
        self.particles = []
        for i in range(50):
            x = i * (self.window_width // 50)
            y = i * (self.window_height // 50)
            self.particles.append([x, y, 1])

        self.animate_particles(canvas)
        return canvas

    def animate_particles(self, canvas):
        """Animate background particles"""
        def update_particles():
            if hasattr(self, 'root') and self.root.winfo_exists():
                canvas.delete("particle")

                for particle in self.particles:
                    particle[0] = (particle[0] + particle[2]) % self.window_width
                    particle[1] = (particle[1] + particle[2] * 0.5) % self.window_height

                    # Draw glowing dot
                    x, y = particle[0], particle[1]
                    canvas.create_oval(x-2, y-2, x+2, y+2,
                                     fill='#00ff88', outline='#4ecdc4',
                                     tags="particle", width=2)

                self.root.after(50, update_particles)

        update_particles()

    def play_sound(self, sound_type="click"):
        """Play a simple click sound"""
        if self.sound_enabled:
            try:
                import pygame
                import numpy as np

                # Create a simple click sound
                duration = 0.1
                sample_rate = 22050
                frequency = 440
                frames = int(duration * sample_rate)
                arr = np.sin(2 * np.pi * frequency * np.linspace(0, duration, frames))
                arr = (arr * 16383).astype(np.int16)
                sound = pygame.sndarray.make_sound(arr)
                sound.set_volume(0.3)
                sound.play()
            except:
                pass

    def create_selection_ui(self):
        """Create the game mode selection interface with glassmorphism effect"""
        # Main container with semi-transparent background
        main_frame = tk.Frame(self.root, bg=palette['background'])
        main_frame.place(relx=0.5, rely=0.5, anchor='center',
                        width=self.window_width-100, height=self.window_height-100)

        # Create glassmorphism background
        glass_canvas = tk.Canvas(main_frame, width=self.window_width-100,
                                height=self.window_height-100,
                                highlightthickness=0, bg=palette['background'])
        glass_canvas.place(x=0, y=0)

        # Draw glassmorphism background
        glass_canvas.create_rectangle(0, 0, self.window_width-100, self.window_height-100,
                                    fill=palette['background'], stipple='gray50', outline=palette['main_box_outline'], width=2)

        # Content frame
        content_frame = tk.Frame(main_frame, bg=palette['background'])
        content_frame.place(relx=0.5, rely=0.5, anchor='center')

        # Enhanced title with glow effect
        title_frame = tk.Frame(content_frame, bg=palette['background'])
        title_frame.pack(pady=(20, 10))

        # Shadow title for glow effect
        shadow_title = tk.Label(title_frame, text="🔬 Infinity Qubit",
                               font=('Arial', 36, 'bold'),
                               fg=palette['shadow_title_color'], bg=palette['background'])
        shadow_title.place(x=3, y=3)

        # Main title
        title_label = tk.Label(title_frame, text="🔬 Infinity Qubit",
                              font=('Arial', 36, 'bold'),
                              fg=palette['title_color'], bg=palette['background'])
        title_label.pack()

        # Enhanced subtitle with animation
        self.subtitle_label = tk.Label(content_frame, text="Choose Your Quantum Adventure",
                                      font=('Arial', 18, 'italic'),
                                      fg=palette['subtitle_color_1'], bg=palette['background'])
        self.subtitle_label.pack(pady=(5, 30))

        # Animate subtitle
        self.animate_subtitle()

        # Game mode buttons container
        buttons_frame = tk.Frame(content_frame, bg=palette['background'])
        buttons_frame.pack(pady=20)

        # Create enhanced game mode buttons
        self.create_enhanced_game_mode_buttons(buttons_frame)

        # Footer with enhanced styling
        footer_frame = tk.Frame(content_frame, bg=palette['background'])
        footer_frame.pack(pady=(30, 20))

        # Enhanced exit button
        exit_btn = tk.Button(footer_frame, text="❌ Exit Game",
                            command=self.exit_game,
                            font=('Arial', 12, 'bold'),
                            bg=palette['exit_button_color'], fg=palette['exit_text_color'],
                            padx=25, pady=10,
                            cursor='hand2',
                            relief=tk.FLAT,
                            bd=0)
        exit_btn.pack(side=tk.RIGHT, padx=10)

        # Version info with enhanced styling
        version_label = tk.Label(footer_frame, text="Version 1.0 | Built with Qiskit & OpenCV",
                                font=('Arial', 10),
                                fg=palette['version_text_color'], bg=palette['background'])
        version_label.pack(side=tk.LEFT)

        # Add hover effects to exit button
        def on_exit_enter(event):
            exit_btn.configure(bg=palette['exit_button_hover_color'])
        def on_exit_leave(event):
            exit_btn.configure(bg=palette['exit_button_color'])

        exit_btn.bind("<Enter>", on_exit_enter)
        exit_btn.bind("<Leave>", on_exit_leave)

    def animate_subtitle(self):
        """Animate subtitle with color cycling"""
        colors = [palette['subtitle_color_1'], palette['subtitle_color_2'], palette['subtitle_color_3'], palette['subtitle_color_4'], palette['subtitle_color_5']]
        color_index = [0]  # Use a list to make it mutable

        def cycle_color():
            if hasattr(self, 'subtitle_label') and self.subtitle_label.winfo_exists():
                self.subtitle_label.configure(fg=colors[color_index[0] % len(colors)])
                color_index[0] += 1
                self.root.after(1500, cycle_color)

        cycle_color()

    def create_enhanced_game_mode_buttons(self, parent):
        """Create enhanced game mode selection buttons with better effects"""
        button_configs = [
            {
                'title': '📚 Tutorial Mode',
                'description': 'Learn quantum gates\nwith an interactive tutorial',
                'color': palette['tutorial_mode_button_color'],
                'hover_color': palette['tutorial_mode_button_hover_color'],
                'command': self.start_tutorial_mode
            },
            {
                'title': '🎮 Puzzle Mode',
                'description': 'Test your skills\nin Puzzle Mode',
                'color': palette['puzzle_mode_button_color'],
                'hover_color': palette['puzzle_mode_button_hover_color'],
                'command': self.start_puzzle_mode
            },
            {
                'title': '🛠️ Sandbox Mode',
                'description': 'Free-form circuit builder\nwith real-time visualization',
                'color': palette['sandbox_mode_button_color'],
                'hover_color': palette['sandbox_mode_button_hover_color'],
                'command': self.start_sandbox_mode
            },
            {
                'title': '🚀 Learn Hub',
                'description': 'Explore more quantum\ncomputing concepts',
                'color': palette['learn_hub_button_color'],
                'hover_color': palette['learn_hub_button_hover_color'],
                'command': self.start_learn_hub_mode
            }
        ]

        # Create buttons in a 2x2 grid
        for i, config in enumerate(button_configs):
            row = i // 2
            col = i % 2

            # Enhanced button frame
            btn_frame = tk.Frame(parent, bg=palette['button_outline_color'], relief=tk.RAISED, bd=2)
            btn_frame.grid(row=row, column=col, padx=15, pady=15, sticky='nsew')

            # Button with enhanced styling
            action_btn = tk.Button(btn_frame,
                                text=f"{config['title']}\n\n{config['description']}",
                                command=lambda cmd=config['command']: self.execute_command(cmd),
                                font=('Arial', 12, 'bold'),
                                bg=config['color'],
                                fg=palette['black'],
                                relief=tk.FLAT,
                                bd=0,
                                cursor='hand2',
                                padx=30,
                                pady=25,
                                justify=tk.CENTER,
                                wraplength=200,
                                width=20,
                                height=5)

            action_btn.pack(fill=tk.BOTH, expand=True)

            # Enhanced hover effects
            def create_hover_effect(btn, original, hover):
                def on_enter(event):
                    btn.configure(bg=hover, relief=tk.RAISED, bd=3)
                def on_leave(event):
                    btn.configure(bg=original, relief=tk.FLAT, bd=0)
                return on_enter, on_leave

            enter_func, leave_func = create_hover_effect(action_btn, config['color'], config['hover_color'])
            action_btn.bind("<Enter>", enter_func)
            action_btn.bind("<Leave>", leave_func)

        # Configure grid weights
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)

    def execute_command(self, command):
        """Execute button command with sound effect"""
        self.play_sound()
        command()

    def start_tutorial_mode(self):
        """Start the tutorial mode"""
        print("📚 Starting Tutorial Mode...")
        try:
            from tutorial import TutorialWindow
            self.stop_video()
            self.root.withdraw()
            TutorialWindow(self.root, self.return_to_main_menu)
        except ImportError as e:
            print(f"❌ Error importing tutorial: {e}")
            messagebox.showerror("Import Error", f"Could not import tutorial module: {e}")
            self.root.deiconify()
        except Exception as e:
            print(f"❌ Error starting tutorial: {e}")
            messagebox.showerror("Error", f"Failed to start tutorial: {e}")
            self.root.deiconify()

    def return_to_main_menu(self):
        """Return to the main menu from tutorial"""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_set()
        # Restart video if available
        if self.video_cap and not self.video_running:
            self.video_running = True
            self.video_thread = threading.Thread(target=self.play_video, daemon=True)
            self.video_thread.start()

    def start_puzzle_mode(self):
        """Start the puzzle mode"""
        print("📚 Starting Puzzle Mode...")
        self.stop_video()
        self.root.destroy()
        try:
            from puzzle_mode import PuzzleMode
            puzzle_root = tk.Tk()
            puzzle_app = PuzzleMode(puzzle_root)
            puzzle_root.mainloop()
        except ImportError:
            print("❌ Puzzle mode module not found")
            messagebox.showerror("Error", "Puzzle mode module not available")
        except Exception as e:
            print(f"❌ Error starting puzzle mode: {e}")
            messagebox.showerror("Error", f"Error starting puzzle mode: {str(e)}")

    def start_sandbox_mode(self):
        """Start the sandbox mode"""
        print("🛠️ Starting Sandbox Mode...")
        self.stop_video()
        self.root.destroy()
        try:
            from sandbox_mode import SandboxMode
            sandbox_root = tk.Tk()
            sandbox_app = SandboxMode(sandbox_root)
            sandbox_root.mainloop()
        except ImportError:
            print("❌ Sandbox module not found")
            messagebox.showerror("Error", "Sandbox module not available")
        except Exception as e:
            print(f"❌ Error starting sandbox: {e}")
            messagebox.showerror("Error", f"Error starting sandbox: {str(e)}")

    def start_learn_hub_mode(self):
        """Start the learn hub mode"""
        print("🚀 Starting Learn Hub...")
        self.stop_video()
        self.root.destroy()
        try:
            from learn_hub import LearnHub
            learn_hub_root = tk.Tk()
            learn_hub_app = LearnHub(learn_hub_root)
            learn_hub_root.mainloop()
        except ImportError:
            print("❌ Learn Hub module not found")
            messagebox.showerror("Error", "Learn Hub module not available")
        except Exception as e:
            print(f"❌ Error starting Learn Hub: {e}")
            messagebox.showerror("Error", f"Error starting Learn Hub: {str(e)}")

    def stop_video(self):
        """Stop video playback"""
        self.video_running = False
        if self.video_cap:
            self.video_cap.release()

    def on_closing(self):
        """Handle window closing"""
        self.stop_video()
        self.root.destroy()
        sys.exit(0)

    def exit_game(self):
        """Exit the game"""
        print("👋 Exiting game...")
        self.play_sound()
        self.stop_video()
        self.root.quit()
        self.root.destroy()
        sys.exit(0)

    def run(self):
        """Run the game mode selection window"""
        self.root.mainloop()

def main():
    """For testing the game mode selection independently"""
    app = GameModeSelection()
    app.run()

if __name__ == "__main__":
    main()
