import { configureStore } from '@reduxjs/toolkit';
// 这里可引入各slice
export const store = configureStore({
  reducer: {
    // user: userReducer,
    // data: dataReducer,
    // report: reportReducer,
    // chat: chatReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch; 