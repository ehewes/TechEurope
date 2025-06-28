import express, { Express, Request, Response } from "express";

const app: Express = express();
const port = process.env.PORT || 3051;

app.use(express.json());

app.get("/demo", (req: Request, res: Response) => {
  res.json({ message: "hello world" });
});

app.listen(port, () => {
  console.log(`Server is running at http://localhost:${port}`);
});

