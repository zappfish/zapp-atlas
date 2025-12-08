import './styles.css';
import { createRoot } from "react-dom/client";
import PhenotypePicker from "./components/ZappForm/PhenotypePicker";

async function main() {

  const el = document.getElementById("root")!;
  const root = createRoot(el);

  root.render(
    <div style={{
      display: "grid",
      gridAutoFlow: "column",
      gridAutoColumns: "1fr",
      height: "100%",
    }}>
      <PhenotypePicker />
    </div>
  );
}

main();
