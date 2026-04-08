<template>
  <div class="app-root app-root--starry">
    <div class="app-background__image" aria-hidden="true"></div>
    <div class="app-background__veil" aria-hidden="true"></div>

    <div class="app-root__view">
      <router-view />
    </div>
  </div>
</template>

<style>
.app-root {
  position: relative;
  min-height: 100vh;
  isolation: isolate;
}

.app-root__view {
  position: relative;
  z-index: 2;
  min-height: 100vh;
}

.app-background__image,
.app-background__veil {
  position: fixed;
  inset: 0;
  pointer-events: none;
}

.app-background__image {
  z-index: 0;
  background-image: url('/backgrounds/night-sky.jpg');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  background-attachment: fixed;
  opacity: 0.96;
  transform: scale(1.02);
}

.app-background__veil {
  z-index: 1;
  background: linear-gradient(180deg, rgba(6, 10, 18, 0.45), rgba(6, 10, 18, 0.62));
}
</style>
