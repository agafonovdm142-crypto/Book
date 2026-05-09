import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AgeGate } from './components/AgeGate';
import { Onboarding } from './components/Onboarding';
import { StoryReader } from './components/StoryReader';

function App() {
  return (
    <BrowserRouter>
      <AgeGate />
      <Onboarding />
      <Routes>
        <Route path="/" element={<StoryReader />} />
        <Route path="/story/:chapterId" element={<StoryReader />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
