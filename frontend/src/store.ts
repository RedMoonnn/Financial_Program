import { configureStore } from '@reduxjs/toolkit';
// 这里可引入各slice
export const store = configureStore({
  reducer: {}, // 空对象
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch; 