if not scene_manager.setting_enter_check and not scene_manager.bag_enter_check:
    self.screen.fill((0, 0, 0))
scene_manager.draw(self.screen)
pg.display.flip()

self.screen.fill((255, 255, 0))
        time.sleep(1.0)
        pg.display.flip()
        self.screen.fill((255, 0, 0))
        time.sleep(1.0)
        pg.display.flip()
