<script setup>
defineProps({
  notifications: {
    type: Array,
    required: true,
  },
})

defineEmits(["dismiss"])
</script>

<template>
  <div
    class="notification-stack"
    aria-live="polite"
    aria-label="Classification notifications"
  >
    <transition-group name="notification">
      <v-card
        v-for="notification in notifications"
        :key="notification.id"
        class="classification-notification"
        elevation="12"
      >
        <div
          class="notification-accent"
          :class="`notification-accent--${notification.type}`"
        />
        <v-card-item>
          <template #prepend>
            <v-avatar
              :color="notification.type === 'success' ? 'success' : 'error'"
              size="38"
            >
              <v-icon
                :icon="
                  notification.type === 'success'
                    ? 'mdi-check'
                    : 'mdi-alert-outline'
                "
              />
            </v-avatar>
          </template>

          <v-card-title class="text-subtitle-1 font-weight-bold">
            {{ notification.title }}
          </v-card-title>
          <v-card-subtitle>{{ notification.filename }}</v-card-subtitle>

          <template #append>
            <v-btn
              icon="mdi-close"
              variant="text"
              size="small"
              aria-label="Dismiss notification"
              @click="$emit('dismiss', notification.id)"
            />
          </template>
        </v-card-item>

        <v-card-text class="pt-0">
          {{ notification.message }}
        </v-card-text>
      </v-card>
    </transition-group>
  </div>
</template>

<style scoped>
.notification-stack {
  position: fixed;
  top: 76px;
  right: 20px;
  z-index: 3000;
  display: grid;
  width: min(380px, calc(100vw - 40px));
  gap: 12px;
  pointer-events: none;
}

.classification-notification {
  position: relative;
  overflow: hidden;
  pointer-events: auto;
}

.classification-notification:hover {
  transform: none;
}

.notification-accent {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  width: 5px;
}

.notification-accent--success {
  background: rgb(var(--v-theme-success));
}

.notification-accent--error {
  background: rgb(var(--v-theme-error));
}

.notification-enter-active,
.notification-leave-active {
  transition: all 180ms ease;
}

.notification-enter-from,
.notification-leave-to {
  opacity: 0;
  transform: translateX(24px);
}

@media (max-width: 600px) {
  .notification-stack {
    top: 68px;
    right: 12px;
    left: 12px;
    width: auto;
  }
}
</style>
