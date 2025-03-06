import { useState } from "react";

import ErrorAlert from "../components/ErrorAlert";
import LinkForm from "../components/LinkForm";
import Loader from "../components/Loader";
import CreatorCard from "../components/CreatorCard";
import BackgroundCard from "../components/BackgroundCard";
import ScoresCard from "../components/ScoresCard";
import CredibilityCard from "../components/CredibilityCard";

import { CreatorInfo } from "../types/interfaces";
import { PROXY_URL } from "../proxy";

export default function CreatorAnalyzer() {
  const [inputLink, setInputLink] = useState<string>("");
  const [creatorInfo, setCreatorInfo] = useState<CreatorInfo | null>(null);
  const [loader, setLoader] = useState<boolean>(false);
  const [alert, setAlert] = useState<string>("");

  const fetchChannelInfo = async (e: React.FormEvent) => {
    e.preventDefault();
    const channelUrl: string = inputLink;

    setInputLink("");
    setCreatorInfo(null);
    setAlert("");
    setLoader(true);

    fetch(PROXY_URL + `/api/get-creator-info?channel_url=${channelUrl}`)
      .then((response) =>
        response
          .json()
          .then((data) => ({ status: response.status, body: data })),
      )
      .then(({ status, body }) => {
        if (status !== 200) {
          throw new Error(body.error);
        }

        setCreatorInfo(body.creator_info);
        setLoader(false);
      })
      .catch((error) => {
        setLoader(false);
        setAlert(error.message);
      });
  };

  return (
    <div className="flex flex-col items-center justify-center gap-5">
      {alert && <ErrorAlert message={alert} setMessage={setAlert} />}

      <LinkForm
        title="Creator Analyzer"
        prompt={
          "Enter the channel link of a creator to assess their performance, credibility, and engagement"
        }
        placeholder={"https://www.youtube.com/@creator"}
        inputLink={inputLink}
        setInputLink={setInputLink}
        onSubmit={fetchChannelInfo}
        submitText="Analyze"
      />

      <Loader loaderTrigger={loader} loaderType={"summary-loader"} />

      {creatorInfo && (
        <div className="flex flex-row flex-wrap justify-center gap-5">
          <CreatorCard
            handle={creatorInfo.handle}
            title={creatorInfo.title}
            statistics={creatorInfo.statistics}
            avatar={creatorInfo.avatar}
            animationDelay={0}
          />
          <ScoresCard
            credibilityScore={creatorInfo.credibilityScore}
            contentQualityScore={creatorInfo.contentQualityScore}
            engagementScore={creatorInfo.engagementScore}
            animationDelay={0.5}
          />
          <BackgroundCard
            background={creatorInfo.background}
            animationDelay={1}
          />
          <CredibilityCard
            credibilityPoints={creatorInfo.credibilityPoints}
            animationDelay={1.5}
          />
        </div>
      )}
    </div>
  );
}
