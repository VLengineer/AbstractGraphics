"""Main game class with game loop and state management."""
import pygame
import moderngl
import numpy as np
from typing import Optional

from .input_handler import InputHandler
from .events import StateManager, GameState
from ..renderer import ShaderManager, Renderer, PostProcessor
from ..world import WorldFactory, World
from ..entities import Player, EntityManager
from ..utils import RandomEventSystem, generate_palette, get_default_palettes


class Game:
    """Main game class managing all systems."""
    
    def __init__(self, width: int = 1280, height: int = 720, fullscreen: bool = False):
        # Initialize pygame
        pygame.init()
        pygame.display.set_caption("Psychedelic Fractal Explorer")
        
        # Display setup
        flags = pygame.FULLSCREEN if fullscreen else 0
        flags |= pygame.OPENGL | pygame.DOUBLEBUF
        self.screen = pygame.display.set_mode((width, height), flags)
        self.width = width
        self.height = height
        
        # ModernGL context
        self.ctx = moderngl.create_context()
        self.ctx.enable(moderngl.BLEND)
        
        # Core systems
        self.input_handler = InputHandler()
        self.state_manager = StateManager(GameState.MENU)
        self.shader_manager = ShaderManager(self.ctx, self._get_shader_dir())
        
        # Renderer
        self.renderer = Renderer(self.ctx, self.shader_manager, width, height)
        self.post_processor = PostProcessor(self.ctx, self.shader_manager, width, height)
        
        # Game systems
        self.player = Player.create()
        self.entity_manager = EntityManager()
        self.event_system = RandomEventSystem(min_interval=15.0, max_interval=45.0)
        
        # World
        self.current_world: Optional[World] = None
        self.world_names = WorldFactory.get_names()
        self.world_index = 0
        self.world_timer = 0.0
        self.world_change_interval = 30.0  # seconds
        self.transition_alpha = 0.0
        self.is_transitioning = False
        
        # Palettes
        self.palettes = get_default_palettes()
        self.palette_index = 0
        self.palette_a, self.palette_b = generate_palette(0.0)
        
        # Timing
        self.clock = pygame.time.Clock()
        self.start_time = 0.0
        self.total_time = 0.0
        
        # Flags
        self.running = True
        self.gravity_flipped = False
        self.in_glitch_zone = False
        
        # Start in menu
        self._setup_menu()
    
    def _get_shader_dir(self) -> str:
        """Get shader directory path."""
        import os
        return os.path.join(os.path.dirname(__file__), '..', 'shaders')
    
    def _setup_menu(self) -> None:
        """Setup menu state."""
        self.current_world = WorldFactory.create('fractal')
        self.current_world.randomize(0.0)
        self.palette_a, self.palette_b = generate_palette(0.0)
    
    def _start_game(self) -> None:
        """Start/restart the game."""
        self.player.reset()
        self.entity_manager.reset()
        self.event_system = RandomEventSystem()
        self.total_time = 0.0
        self.world_timer = 0.0
        self.gravity_flipped = False
        self.in_glitch_zone = False
        
        # Start with random world
        self.world_index = np.random.randint(0, len(self.world_names))
        self.current_world = WorldFactory.create(self.world_names[self.world_index])
        self.current_world.randomize()
        self.palette_a, self.palette_b = generate_palette(np.random.random())
        
        # Spawn initial entities
        for _ in range(5):
            self.entity_manager.spawn_orb()
        for _ in range(2):
            self.entity_manager.spawn_hostile(
                np.random.uniform(-10, 10, 3).astype(np.float32),
                self.player.position
            )
    
    def _switch_world(self, target_name: Optional[str] = None) -> None:
        """Switch to a different world."""
        if target_name:
            self.world_index = self.world_names.index(target_name)
        else:
            self.world_index = (self.world_index + 1) % len(self.world_names)
        
        self.is_transitioning = True
        self.transition_alpha = 0.0
    
    def _complete_world_switch(self) -> None:
        """Complete world transition."""
        self.current_world = WorldFactory.create(self.world_names[self.world_index])
        self.current_world.randomize()
        self.is_transitioning = False
        self.palette_a, self.palette_b = generate_palette(np.random.random())
    
    def handle_events(self) -> None:
        """Process pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            self.input_handler.handle_event(event)
            
            # Handle key presses for state transitions
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state_manager.is_playing():
                        self.state_manager.to_pause()
                    elif self.state_manager.is_paused():
                        self.state_manager.to_play()
                
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if self.state_manager.is_menu():
                        self._start_game()
                        self.state_manager.to_play()
                    elif self.state_manager.is_gameover():
                        pass  # R is for restart
                
                elif event.key == pygame.K_r:
                    if self.state_manager.is_gameover():
                        self._start_game()
                        self.state_manager.to_play()
                
                elif event.key == pygame.K_f:
                    self.toggle_fullscreen()
                
                elif event.key == pygame.K_TAB:
                    if self.state_manager.is_playing():
                        self._switch_world()
                
                elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                    idx = event.key - pygame.K_1
                    self.palette_a, self.palette_b = self.palettes[idx]
                
                elif event.key == pygame.K_SPACE:
                    if self.state_manager.is_playing():
                        if self.player.dash():
                            # Flash effect - push back hostiles
                            for hostile in self.entity_manager.hostiles:
                                direction = hostile.position - self.player.position
                                dist = np.linalg.norm(direction)
                                if dist > 0:
                                    hostile.velocity = (direction / dist) * 10.0
    
    def toggle_fullscreen(self) -> None:
        """Toggle fullscreen mode."""
        current_flags = self.screen.get_flags()
        if current_flags & pygame.FULLSCREEN:
            self.screen = pygame.display.set_mode(
                (self.width, self.height), 
                pygame.OPENGL | pygame.DOUBLEBUF
            )
        else:
            self.screen = pygame.display.set_mode(
                (0, 0),
                pygame.OPENGL | pygame.DOUBLEBUF | pygame.FULLSCREEN
            )
            self.width, self.height = self.screen.get_size()
            self.renderer.resize(self.width, self.height)
            self.post_processor.resize(self.width, self.height)
    
    def update(self, dt: float) -> None:
        """Update game logic."""
        input_state = self.input_handler.update()
        
        # Menu state - just animate
        if self.state_manager.is_menu():
            self.total_time += dt
            if self.current_world:
                self.current_world.update(dt, self.player.position, self.total_time)
            return
        
        # Game over state
        if self.state_manager.is_gameover():
            return
        
        # Paused state
        if self.state_manager.is_paused():
            return
        
        # Playing state
        if self.state_manager.is_playing():
            self.total_time += dt
            
            # Check for world change
            self.world_timer += dt
            if self.world_timer >= self.world_change_interval and not self.is_transitioning:
                self._switch_world()
                self.world_timer = 0.0
            
            # Handle transition
            if self.is_transitioning:
                self.transition_alpha += dt * 2.0
                if self.transition_alpha >= 1.0:
                    self._complete_world_switch()
                    self.transition_alpha = 1.0
            
            # Update event system
            new_event = self.event_system.update(dt)
            if new_event:
                self._handle_event_start(new_event)
            
            # Apply active event effects
            active_event = self.event_system.active_event
            if active_event:
                self._apply_event_effects(active_event, dt)
            
            # Update player
            self.player.update(dt, input_state, self.gravity_flipped)
            
            # Update entities
            entity_events = self.entity_manager.update(dt, self.player.position)
            
            # Handle entity events
            if entity_events['orbs_collected'] > 0:
                self.player.add_score(entity_events['orbs_collected'])
            
            if entity_events['damage_taken'] > 0:
                self.player.take_damage(entity_events['damage_taken'])
                if not self.player.is_alive:
                    self.state_manager.to_gameover()
            
            if entity_events['portal_entered']:
                self._switch_world(entity_events['portal_entered'])
            
            self.in_glitch_zone = entity_events['in_glitch_zone']
            
            # Update world
            if self.current_world:
                self.current_world.update(dt, self.player.position, self.total_time)
            
            # Spawn entities periodically
            if np.random.random() < 0.02:  # 2% chance per frame
                self.entity_manager.spawn_orb()
            if np.random.random() < 0.005:  # 0.5% chance per frame
                self.entity_manager.spawn_hostile(
                    np.random.uniform(-10, 10, 3).astype(np.float32),
                    self.player.position
                )
    
    def _handle_event_start(self, event) -> None:
        """Handle start of a random event."""
        print(f"Event started: {event}")
        
        if event.type.name == "GRAVITY_FLIP":
            self.gravity_flipped = True
        elif event.type.name == "COLOR_INVERT":
            self.post_processor.bloom_threshold = 0.2  # More bloom = inverted look
    
    def _apply_event_effects(self, event, dt: float) -> None:
        """Apply ongoing event effects."""
        intensity = event.intensity
        self.post_processor.set_event_intensity(intensity)
        
        # Randomize palette during palette shift
        if event.type.name == "PALETTE_SHIFT":
            t = self.total_time * 2.0
            self.palette_a = np.array([
                0.5 + 0.5 * np.sin(t),
                0.5 + 0.5 * np.sin(t + 1.0),
                0.5 + 0.5 * np.sin(t + 2.0),
                0.5 + 0.5 * np.sin(t + 3.0),
            ], dtype=np.float32)
            self.palette_b = np.array([
                0.5 + 0.5 * np.cos(t),
                0.5 + 0.5 * np.cos(t + 1.0),
                0.5 + 0.5 * np.cos(t + 2.0),
                0.5 + 0.5 * np.cos(t + 3.0),
            ], dtype=np.float32)
        
        # Reset gravity when event ends
        if event.type.name == "GRAVITY_FLIP":
            pass  # Will reset when event ends
    
    def render(self) -> None:
        """Render the game."""
        resolution = (float(self.width), float(self.height))
        mouse = (
            self.input_handler.mouse_pos[0] / self.width - 0.5,
            self.input_handler.mouse_pos[1] / self.height - 0.5
        )
        
        # Render world
        if self.current_world:
            # Get camera info for SDF world
            camera_pos = self.player.position.astype(np.float32)
            camera_dir = self.player.get_forward_vector().astype(np.float32)
            
            # Get event intensity for visual effects
            event_intensity = 0.0
            if self.active_event:
                event_intensity = min(1.0, self.active_event.timer / 3.0)  # Peak at start
            
            self.current_world.render(
                self.renderer, 
                self.total_time, 
                resolution, 
                mouse,
                self.palette_a, 
                self.palette_b,
                camera_pos=camera_pos,
                camera_dir=camera_dir,
                event_intensity=event_intensity
            )
        
        # Get render texture and apply post-processing
        render_tex = self.renderer.get_render_texture()
        self.post_processor.render(render_tex)
        
        # Blit to screen
        final_tex = self.post_processor.current_texture
        self.ctx.screen.use()
        self.ctx.screen.clear(0.0, 0.0, 0.0, 1.0)
        final_tex.use(0)
        
        # Draw textured quad to screen
        vertices = np.array([-1, -1, 1, -1, -1, 1, 1, 1], dtype='f4')
        vbo = self.ctx.buffer(vertices.tobytes())
        
        # Simple blit program
        blit_prog = self.ctx.program(
            vertex_shader="""
                #version 330
                in vec2 in_vert;
                out vec2 uv;
                void main() {
                    uv = in_vert * 0.5 + 0.5;
                    gl_Position = vec4(in_vert, 0.0, 1.0);
                }
            """,
            fragment_shader="""
                #version 330
                uniform sampler2D tex;
                in vec2 uv;
                out vec4 color;
                void main() {
                    color = texture(tex, uv);
                }
            """
        )
        
        vao = self.ctx.vertex_array(blit_prog, [(vbo, '2f', 'in_vert')])
        vao.render(moderngl.TRIANGLE_STRIP)
        
        # Draw UI overlay
        self._render_ui()
        
        pygame.display.flip()
    
    def _render_ui(self) -> None:
        """Render UI overlay using pygame."""
        # This would use pygame font rendering
        # For now, skip complex UI
        pass
    
    def run(self) -> None:
        """Main game loop."""
        self.start_time = pygame.time.get_ticks() / 1000.0
        
        while self.running:
            dt = self.clock.tick(60) / 1000.0  # Cap at 60 FPS
            
            self.handle_events()
            self.update(dt)
            self.render()
            
            self.state_manager.update()
        
        pygame.quit()


def main():
    """Entry point."""
    game = Game(fullscreen=False)
    game.run()


if __name__ == '__main__':
    main()
